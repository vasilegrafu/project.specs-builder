#!/usr/bin/env python3
"""Stock sync: every night, take the supplier's stock feed and bring the shop's stock in line with it.

    python stock_sync.py                 # one run, as the timer starts it
    python stock_sync.py --dry-run       # read, compare, report; change nothing
    python stock_sync.py --feed FILE     # a feed file instead of the supplier's address, for a rerun by hand

What it does, in order: fetch the feed (a CSV of SKU, quantity, as-of time) from the supplier; refuse a feed that is
stale, empty or out of shape; compare it with the shop's stock, SKU by SKU; refuse the whole run where the change is
too large to be real; write the new quantities to the catalogue; write the report; mail the report where anything
is low or the run failed. One run at a time: a lock file holds the next one off. Exit codes: 0 done, 1 nothing to
do, 2 the feed was refused, 3 the catalogue would not take the writes, 4 another run holds the lock.
"""
from __future__ import annotations

import argparse
import csv
import io
import logging
import os
import smtplib
import sys
import time
import tomllib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
CONFIG = tomllib.loads((HERE / "config.toml").read_text(encoding="utf-8"))
LOCK = HERE / "stock_sync.lock"
RETRIES = 3                        # of the fetch, ten minutes apart; then the run fails and the morning gets a mail
RETRY_AFTER_SECONDS = 600
FEED_STALE_AFTER_HOURS = 36        # a feed older than this is last night's, repeated: refused
MAX_CHANGE_RATIO = 0.5             # more than half the SKUs changing at once is a broken feed, not a stock take
LOW_STOCK_AT = CONFIG["thresholds"]["low_stock_at"]
TIMEOUT_SECONDS = 30

log = logging.getLogger("stock_sync")


class FeedRefused(Exception):
    """The feed cannot be used, and why."""


def fetch_feed(address: str) -> str:
    """The feed's text, tried three times ten minutes apart. The supplier answers 503 while they rebuild it."""
    for attempt in range(1, RETRIES + 1):
        try:
            answer = httpx.get(address, timeout=TIMEOUT_SECONDS,
                               headers={"Authorization": f"Bearer {os.environ['SUPPLIER_FEED_TOKEN']}"})
            if answer.status_code == 200:
                return answer.text
            log.warning("feed answered %d on try %d", answer.status_code, attempt)
        except httpx.HTTPError as problem:
            log.warning("feed could not be fetched on try %d: %s", attempt, problem)
        if attempt < RETRIES:
            time.sleep(RETRY_AFTER_SECONDS)
    raise FeedRefused(f"the feed could not be fetched in {RETRIES} tries")


def parse_feed(text: str, now: datetime) -> dict[str, int]:
    """SKU → quantity. Refused: no rows, a missing column, a quantity that is not a whole number, a feed older
    than FEED_STALE_AFTER_HOURS. A SKU listed twice takes the last row, and is logged."""
    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows:
        raise FeedRefused("the feed has no rows")
    for column in ("sku", "quantity", "as_of"):
        if column not in rows[0]:
            raise FeedRefused(f"the feed has no column {column}")
    as_of = datetime.fromisoformat(rows[0]["as_of"]).astimezone(timezone.utc)
    if now - as_of > timedelta(hours=FEED_STALE_AFTER_HOURS):
        raise FeedRefused(f"the feed is from {as_of:%Y-%m-%d %H:%M}, older than {FEED_STALE_AFTER_HOURS} hours")
    stock: dict[str, int] = {}
    for n, row in enumerate(rows, start=2):
        try:
            qty = int(row["quantity"])
        except ValueError as problem:
            raise FeedRefused(f"line {n}: quantity {row['quantity']!r} is not a whole number") from problem
        if qty < 0:
            raise FeedRefused(f"line {n}: quantity {qty} is below zero")
        if row["sku"] in stock:
            log.info("line %d: %s listed again; the last row wins", n, row["sku"])
        stock[row["sku"]] = qty
    return stock


def shop_stock() -> dict[str, int]:
    """What the catalogue holds today, SKU → quantity, from its API."""
    answer = httpx.get(f"{CONFIG['catalogue']['address']}/stock", timeout=TIMEOUT_SECONDS,
                       headers={"Authorization": f"Bearer {os.environ['CATALOGUE_TOKEN']}"})
    answer.raise_for_status()
    return {row["sku"]: row["quantity"] for row in answer.json()["items"]}


def compare(feed: dict[str, int], shop: dict[str, int]) -> dict[str, tuple[int, int]]:
    """SKU → (before, after) for every SKU whose quantity differs. A SKU the shop does not sell is passed over and
    counted; a SKU the feed does not carry keeps the shop's number."""
    changes = {}
    unknown = 0
    for sku, qty in feed.items():
        if sku not in shop:
            unknown += 1
            continue
        if shop[sku] != qty:
            changes[sku] = (shop[sku], qty)
    if unknown:
        log.info("%d SKU(s) of the feed are not sold by the shop", unknown)
    if shop and len(changes) / len(shop) > MAX_CHANGE_RATIO:
        raise FeedRefused(f"{len(changes)} of {len(shop)} SKUs would change: more than {MAX_CHANGE_RATIO:.0%}, "
                          "which no stock take does; the feed is held to be broken")
    return changes


def write_changes(changes: dict[str, tuple[int, int]]) -> None:
    """One PATCH per SKU to the catalogue. A refusal stops the run; what was written stays written, and the report
    says how far it got."""
    for sku, (_, after) in changes.items():
        answer = httpx.patch(f"{CONFIG['catalogue']['address']}/stock/{sku}", json={"quantity": after},
                             timeout=TIMEOUT_SECONDS,
                             headers={"Authorization": f"Bearer {os.environ['CATALOGUE_TOKEN']}"})
        if answer.status_code != 200:
            raise RuntimeError(f"the catalogue refused {sku}: {answer.status_code} {answer.text[:120]}")


def report(changes: dict[str, tuple[int, int]], feed: dict[str, int], now: datetime, outcome: str) -> str:
    low = sorted(sku for sku, qty in feed.items() if 0 < qty <= LOW_STOCK_AT)
    out = sorted(sku for sku, qty in feed.items() if qty == 0)
    lines = [f"Stock sync {now:%Y-%m-%d %H:%M} UTC: {outcome}", f"{len(changes)} SKU(s) changed",
             f"{len(low)} low (at or under {LOW_STOCK_AT}): {', '.join(low) or 'none'}",
             f"{len(out)} out of stock: {', '.join(out) or 'none'}", ""]
    lines += [f"{sku}: {before} → {after}" for sku, (before, after) in sorted(changes.items())]
    return "\n".join(lines) + "\n"


def mail(subject: str, body: str) -> None:
    """The morning's mail, to the address in config.toml, through the shop's own relay."""
    message = EmailMessage()
    message["From"] = CONFIG["mail"]["from"]
    message["To"] = CONFIG["mail"]["to"]
    message["Subject"] = subject
    message.set_content(body)
    with smtplib.SMTP(CONFIG["mail"]["relay"], timeout=TIMEOUT_SECONDS) as relay:
        relay.send_message(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bring the shop's stock in line with the supplier's feed.")
    parser.add_argument("--dry-run", action="store_true", help="read and compare; write and mail nothing")
    parser.add_argument("--feed", type=Path, help="a feed file to read in place of the supplier's address")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.StreamHandler(sys.stdout),
                                  logging.FileHandler(HERE / "logs" / f"{datetime.now():%Y-%m-%d}.log")])
    if LOCK.exists() and time.time() - LOCK.stat().st_mtime < 6 * 3600:
        log.error("another run holds the lock, %s; if none is running, remove it (RUNBOOK.md)", LOCK)
        return 4
    LOCK.write_text(str(os.getpid()))
    now = datetime.now(timezone.utc)
    try:
        text = args.feed.read_text(encoding="utf-8") if args.feed else fetch_feed(CONFIG["supplier"]["feed"])
        feed = parse_feed(text, now)
        changes = compare(feed, shop_stock())
        if not changes:
            log.info("nothing to do: the shop's stock matches the feed")
            return 1
        if args.dry_run:
            print(report(changes, feed, now, "dry run, nothing written"))
            return 0
        write_changes(changes)
        said = report(changes, feed, now, "done")
        (HERE / "reports" / f"{now:%Y-%m-%d}.txt").write_text(said, encoding="utf-8")
        if any(0 <= qty <= LOW_STOCK_AT for qty in feed.values()):
            mail(f"Stock sync {now:%Y-%m-%d}: low stock", said)
        log.info("done: %d SKU(s) changed", len(changes))
        return 0
    except FeedRefused as problem:
        log.error("the feed was refused: %s", problem)
        mail(f"Stock sync {now:%Y-%m-%d} FAILED: the feed was refused", f"{problem}\n\nSee RUNBOOK.md.")
        return 2
    except RuntimeError as problem:
        log.error("the run stopped: %s", problem)
        mail(f"Stock sync {now:%Y-%m-%d} FAILED: the catalogue refused a write", f"{problem}\n\nSee RUNBOOK.md.")
        return 3
    finally:
        LOCK.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
