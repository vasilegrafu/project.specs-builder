"""Parcelpost: the API a shop calls to send parcels. Every route is here; what each keeps is in models.py."""
from __future__ import annotations

import secrets
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

from . import webhooks
from .auth import Key, caller, needs
from .models import (Address, EventKind, Parcel, Service, Shipment, ShipmentStatus, Subscription,
                     TrackingEvent)

app = FastAPI(title="Parcelpost API", version="2026-10")

MAX_WEIGHT_KG = 30.0               # heavier parcels go by freight, not here
MAX_SIDE_CM = 120                  # the longest side
MAX_GIRTH_CM = 300                 # length + 2 × (width + height)
ECONOMY_MAX_WEIGHT_KG = 20.0       # economy takes less
COUNTRIES = {"DE", "AT", "NL", "BE", "FR", "LU", "DK", "PL", "CZ"}   # where Parcelpost delivers today
PAGE_SIZE = 50
RATE_LIMIT_PER_MINUTE = 600        # per key; past it the answer is 429 with Retry-After

SHIPMENTS: dict[str, Shipment] = {}
SUBSCRIPTIONS: dict[str, Subscription] = {}


# --- what a call sends -----------------------------------------------------------------------------------------

class AddressIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    street: str = Field(min_length=1, max_length=120)
    city: str = Field(min_length=1, max_length=60)
    postcode: str = Field(min_length=3, max_length=10)
    country: str = Field(min_length=2, max_length=2)
    phone: str = ""


class ParcelIn(BaseModel):
    weight_kg: float = Field(gt=0, le=MAX_WEIGHT_KG)
    length_cm: int = Field(gt=0, le=MAX_SIDE_CM)
    width_cm: int = Field(gt=0, le=MAX_SIDE_CM)
    height_cm: int = Field(gt=0, le=MAX_SIDE_CM)
    contents: str = Field(default="", max_length=200)


class ShipmentIn(BaseModel):
    service: Service = Service.STANDARD
    sender: AddressIn
    recipient: AddressIn
    parcel: ParcelIn
    reference: str = Field(default="", max_length=40)


class SubscriptionIn(BaseModel):
    url: str = Field(pattern=r"^https://")
    events: list[str] = Field(min_length=1)


def shipment_out(s: Shipment) -> dict:
    return {"id": s.id, "status": s.status.value, "service": s.service.value, "reference": s.reference,
            "created_at": s.created_at.isoformat(timespec="seconds") + "Z", "label_url": s.label_url or None,
            "recipient": {"name": s.recipient.name, "city": s.recipient.city, "country": s.recipient.country},
            "tracking_url": f"https://track.parcelpost.example/{s.id}"}


def own(shipment_id: str, key: Key) -> Shipment:
    """The shipment, where it is the caller's; another account's is 404, as one that does not exist."""
    shipment = SHIPMENTS.get(shipment_id)
    if shipment is None or shipment.account != key.account:
        raise HTTPException(status_code=404, detail={"error": "no shipment has that id"})
    return shipment


# --- shipments ----------------------------------------------------------------------------------------------------

@app.post("/v1/shipments", status_code=201)
def create_shipment(body: ShipmentIn, key: Key = Depends(caller)) -> dict:
    """Register a parcel to send. Nothing moves until a label is produced and the parcel handed over."""
    needs(key, "shipments:write")
    if body.recipient.country not in COUNTRIES:
        raise HTTPException(status_code=422, detail={"error": f"Parcelpost does not deliver to {body.recipient.country}",
                                                     "field": "recipient.country"})
    girth = body.parcel.length_cm + 2 * (body.parcel.width_cm + body.parcel.height_cm)
    if girth > MAX_GIRTH_CM:
        raise HTTPException(status_code=422, detail={"error": f"the parcel's girth is {girth} cm; {MAX_GIRTH_CM} cm is the most",
                                                     "field": "parcel"})
    if body.service == Service.ECONOMY and body.parcel.weight_kg > ECONOMY_MAX_WEIGHT_KG:
        raise HTTPException(status_code=422, detail={"error": f"economy takes up to {ECONOMY_MAX_WEIGHT_KG} kg; choose standard",
                                                     "field": "service"})
    shipment = Shipment(id="PP-" + "".join(secrets.choice("0123456789") for _ in range(12)), account=key.account,
                        service=body.service, sender=Address(**body.sender.model_dump()),
                        recipient=Address(**body.recipient.model_dump()), parcel=Parcel(**body.parcel.model_dump()),
                        reference=body.reference)
    shipment.events.append(TrackingEvent(datetime.utcnow(), EventKind.STATUS, ShipmentStatus.CREATED, "Parcelpost",
                                         "Shipment registered"))
    SHIPMENTS[shipment.id] = shipment
    return shipment_out(shipment)


@app.get("/v1/shipments")
def list_shipments(status: ShipmentStatus | None = None, reference: str | None = None, page: int = 1,
                   key: Key = Depends(caller)) -> dict:
    """The account's shipments, newest first, fifty to a page."""
    needs(key, "shipments:read")
    mine = [s for s in SHIPMENTS.values() if s.account == key.account
            and (status is None or s.status == status) and (reference is None or s.reference == reference)]
    mine.sort(key=lambda s: s.created_at, reverse=True)
    start = (page - 1) * PAGE_SIZE
    return {"items": [shipment_out(s) for s in mine[start:start + PAGE_SIZE]], "page": page, "total": len(mine)}


@app.get("/v1/shipments/{shipment_id}")
def get_shipment(shipment_id: str, key: Key = Depends(caller)) -> dict:
    """One shipment, as it stands."""
    needs(key, "shipments:read")
    return shipment_out(own(shipment_id, key))


@app.get("/v1/shipments/{shipment_id}/events")
def tracking(shipment_id: str, key: Key = Depends(caller)) -> dict:
    """Every event of the shipment, oldest first: what the recipient's tracking page shows."""
    needs(key, "shipments:read")
    shipment = own(shipment_id, key)
    return {"id": shipment.id, "status": shipment.status.value,
            "events": [{"at": e.at.isoformat(timespec="seconds") + "Z", "kind": e.kind.value,
                        "status": e.status.value if e.status else None, "place": e.place, "text": e.text}
                       for e in shipment.events]}


@app.post("/v1/shipments/{shipment_id}/label")
def produce_label(shipment_id: str, key: Key = Depends(caller)) -> dict:
    """Produce the label: a PDF, A6, with the barcode the courier scans. Once produced, the same label is answered
    again; a cancelled shipment has none."""
    needs(key, "labels")
    shipment = own(shipment_id, key)
    if shipment.status == ShipmentStatus.CANCELLED:
        raise HTTPException(status_code=409, detail={"error": "the shipment is cancelled; it has no label"})
    if not shipment.label_url:
        shipment.label_url = f"https://labels.parcelpost.example/{shipment.id}.pdf"
        shipment.status = ShipmentStatus.LABELLED
        shipment.events.append(TrackingEvent(datetime.utcnow(), EventKind.STATUS, ShipmentStatus.LABELLED,
                                             "Parcelpost", "Label produced"))
        notify("shipment.status.changed", shipment)
    return {"id": shipment.id, "label_url": shipment.label_url, "format": "A6", "test": key.test}


@app.delete("/v1/shipments/{shipment_id}", status_code=204)
def cancel_shipment(shipment_id: str, key: Key = Depends(caller)) -> Response:
    """Cancel before collection. A collected parcel cannot be cancelled: ask for a return instead."""
    needs(key, "shipments:write")
    shipment = own(shipment_id, key)
    if not shipment.can_cancel():
        raise HTTPException(status_code=409, detail={"error": f"the shipment is {shipment.status.value}; only one "
                                                              "not yet collected can be cancelled"})
    shipment.status = ShipmentStatus.CANCELLED
    shipment.events.append(TrackingEvent(datetime.utcnow(), EventKind.STATUS, ShipmentStatus.CANCELLED,
                                         "Parcelpost", "Cancelled by the sender"))
    notify("shipment.status.changed", shipment)
    return Response(status_code=204)


# --- webhooks -----------------------------------------------------------------------------------------------------

@app.post("/v1/webhooks", status_code=201)
def subscribe(body: SubscriptionIn, key: Key = Depends(caller)) -> dict:
    """Ask to be told of events at an https address. The secret that signs each delivery is answered once."""
    needs(key, "webhooks")
    unknown = [e for e in body.events if e not in webhooks.EVENTS]
    if unknown:
        raise HTTPException(status_code=422, detail={"error": f"no such event: {', '.join(unknown)}", "field": "events"})
    subscription = Subscription(id="WH-" + secrets.token_hex(4), account=key.account, url=body.url,
                                events=body.events, secret=secrets.token_hex(24))
    SUBSCRIPTIONS[subscription.id] = subscription
    return {"id": subscription.id, "url": subscription.url, "events": subscription.events,
            "secret": subscription.secret, "active": True}


@app.get("/v1/webhooks")
def list_subscriptions(key: Key = Depends(caller)) -> dict:
    needs(key, "webhooks")
    return {"items": [{"id": s.id, "url": s.url, "events": s.events, "active": s.active, "failures": s.failures}
                      for s in SUBSCRIPTIONS.values() if s.account == key.account]}


@app.delete("/v1/webhooks/{subscription_id}", status_code=204)
def unsubscribe(subscription_id: str, key: Key = Depends(caller)) -> Response:
    needs(key, "webhooks")
    subscription = SUBSCRIPTIONS.get(subscription_id)
    if subscription is None or subscription.account != key.account:
        raise HTTPException(status_code=404, detail={"error": "no subscription has that id"})
    del SUBSCRIPTIONS[subscription_id]
    return Response(status_code=204)


def notify(event: str, shipment: Shipment) -> None:
    """Every active subscription of the account that asked for the event gets one delivery."""
    for subscription in SUBSCRIPTIONS.values():
        if subscription.account == shipment.account:
            webhooks.deliver(subscription, event, shipment)
