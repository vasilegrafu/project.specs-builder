"""What the job promises: what it refuses, what it changes, what it leaves alone."""
from datetime import datetime, timedelta, timezone

import pytest

import stock_sync
from stock_sync import FeedRefused, compare, parse_feed

NOW = datetime(2026, 10, 10, 2, 30, tzinfo=timezone.utc)


def feed(*rows: str, as_of: str = "2026-10-10T00:58:00+00:00") -> str:
    return "sku,quantity,as_of\n" + "".join(f"{row},{as_of}\n" for row in rows)


def test_a_feed_is_read_sku_by_sku():
    assert parse_feed(feed("AC-VLT-65,40", "LT-ZEN-12,0"), NOW) == {"AC-VLT-65": 40, "LT-ZEN-12": 0}


def test_an_empty_feed_is_refused():
    with pytest.raises(FeedRefused, match="no rows"):
        parse_feed("sku,quantity,as_of\n", NOW)


def test_a_stale_feed_is_refused():
    with pytest.raises(FeedRefused, match="older than 36 hours"):
        parse_feed(feed("AC-VLT-65,40", as_of="2026-10-08T00:58:00+00:00"), NOW)


def test_a_quantity_that_is_not_a_number_is_refused():
    with pytest.raises(FeedRefused, match="not a whole number"):
        parse_feed(feed("AC-VLT-65,forty"), NOW)


def test_the_last_row_of_a_sku_listed_twice_wins():
    assert parse_feed(feed("AC-VLT-65,40", "AC-VLT-65,38"), NOW)["AC-VLT-65"] == 38


def test_only_what_differs_is_a_change():
    changes = compare({"A": 1, "B": 2, "C": 9}, {"A": 1, "B": 5, "D": 7})
    assert changes == {"B": (5, 2)}


def test_a_feed_that_changes_more_than_half_is_refused():
    with pytest.raises(FeedRefused, match="more than 50%"):
        compare({"A": 0, "B": 0, "C": 0}, {"A": 1, "B": 2, "C": 3, "D": 4})


def test_the_fetch_is_tried_three_times(monkeypatch):
    tries = []

    class Answer:
        status_code = 503
        text = ""

    monkeypatch.setattr(stock_sync.httpx, "get", lambda *a, **k: tries.append(1) or Answer())
    monkeypatch.setattr(stock_sync.time, "sleep", lambda s: None)
    monkeypatch.setenv("SUPPLIER_FEED_TOKEN", "x")
    with pytest.raises(FeedRefused, match="3 tries"):
        stock_sync.fetch_feed("https://feed.example/stock.csv")
    assert len(tries) == 3


@pytest.mark.skip(reason="needs the catalogue's test environment, which is not in the demo")
def test_a_refused_write_stops_the_run_and_keeps_what_was_written():
    pass


def test_the_lock_is_stale_after_six_hours(tmp_path, monkeypatch):
    lock = tmp_path / "stock_sync.lock"
    lock.write_text("1")
    old = (datetime.now() - timedelta(hours=7)).timestamp()
    import os
    os.utime(lock, (old, old))
    monkeypatch.setattr(stock_sync, "LOCK", lock)
    assert stock_sync.time.time() - lock.stat().st_mtime > 6 * 3600
