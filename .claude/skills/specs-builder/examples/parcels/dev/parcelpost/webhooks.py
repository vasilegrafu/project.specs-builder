"""What Parcelpost sends: one HTTP POST per event to each subscription that asked for it, signed, tried again."""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
from datetime import datetime

import httpx

from .models import Shipment, Subscription

log = logging.getLogger("parcelpost.webhooks")

RETRY_AFTER_SECONDS = (60, 300, 1800, 7200, 21600)   # five more tries over six hours, then the delivery is dropped
PAUSE_AT_FAILURES = 10                                # subscriptions that fail ten deliveries in a row are paused
TIMEOUT_SECONDS = 10
EVENTS = ("shipment.status.changed", "shipment.delivery.attempted")


def payload(event: str, shipment: Shipment) -> dict:
    """What a subscriber receives. Never the sender's or the recipient's address: the subscriber has those."""
    return {
        "event": event,
        "sent_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "shipment": {"id": shipment.id, "reference": shipment.reference, "status": shipment.status.value,
                     "service": shipment.service.value},
        "last_event": {"at": shipment.events[-1].at.isoformat(timespec="seconds") + "Z",
                       "kind": shipment.events[-1].kind.value, "place": shipment.events[-1].place,
                       "text": shipment.events[-1].text} if shipment.events else None,
    }


def signature(secret: str, body: bytes) -> str:
    """`X-Parcelpost-Signature: sha256=<hex>`: an HMAC of the body with the subscription's secret."""
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def deliver(subscription: Subscription, event: str, shipment: Shipment, attempt: int = 0) -> bool:
    """One try. A 2xx answer within ten seconds is a delivery; anything else is tried again later, and counted."""
    if not subscription.active or event not in subscription.events:
        return False
    body = json.dumps(payload(event, shipment), separators=(",", ":")).encode()
    headers = {"Content-Type": "application/json", "X-Parcelpost-Signature": signature(subscription.secret, body),
               "X-Parcelpost-Event": event, "X-Parcelpost-Attempt": str(attempt + 1)}
    try:
        answer = httpx.post(subscription.url, content=body, headers=headers, timeout=TIMEOUT_SECONDS)
        ok = 200 <= answer.status_code < 300
    except httpx.HTTPError as problem:
        log.warning("webhook %s to %s failed: %s", subscription.id, subscription.url, problem)
        ok = False
    if ok:
        subscription.failures = 0
        return True
    subscription.failures += 1
    if subscription.failures >= PAUSE_AT_FAILURES:
        subscription.active = False
        log.error("webhook %s paused after %d failures in a row", subscription.id, subscription.failures)
    elif attempt < len(RETRY_AFTER_SECONDS):
        schedule_retry(subscription, event, shipment, attempt + 1, RETRY_AFTER_SECONDS[attempt])
    return False


def schedule_retry(subscription: Subscription, event: str, shipment: Shipment, attempt: int, after: int) -> None:
    """Hand the next try to the queue; the worker calls deliver() again after `after` seconds."""
    log.info("webhook %s: try %d in %ds", subscription.id, attempt + 1, after)
