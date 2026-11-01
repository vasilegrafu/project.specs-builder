"""What Parcelpost keeps: a shipment, its events, a label, a webhook subscription."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ShipmentStatus(str, Enum):
    """Where a shipment is in its life. It moves forward only; cancelled is an end, as delivered and returned are."""
    CREATED = "created"            # registered, no label yet
    LABELLED = "labelled"          # a label has been produced; the parcel can be handed over
    COLLECTED = "collected"        # the courier has it
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    RETURNED = "returned"          # could not be delivered after three attempts, or refused
    CANCELLED = "cancelled"        # by the sender, before collection


class Service(str, Enum):
    STANDARD = "standard"          # two to four working days
    EXPRESS = "express"            # the next working day, handed over before 16:00
    ECONOMY = "economy"            # five to eight working days, 30 kg at most, no signature


class EventKind(str, Enum):
    STATUS = "status"              # the status changed
    SCAN = "scan"                  # seen at a depot or in a van; the status is unchanged
    ATTEMPT = "attempt"            # a delivery was tried and not made
    NOTE = "note"                  # the courier's remark: left with a neighbour, a safe place


@dataclass
class Address:
    name: str
    street: str
    city: str
    postcode: str
    country: str                   # ISO 3166-1 alpha-2: DE, FR, NL
    phone: str = ""


@dataclass
class Parcel:
    weight_kg: float
    length_cm: int
    width_cm: int
    height_cm: int
    contents: str = ""             # what is in it, in the sender's words; shown on the label for customs only


@dataclass
class TrackingEvent:
    at: datetime
    kind: EventKind
    status: ShipmentStatus | None  # set for a STATUS event; None for a scan, an attempt or a note
    place: str                     # the depot or the town
    text: str                      # the line the recipient reads: "Out for delivery"


@dataclass
class Shipment:
    id: str                        # PP-<12 digits>, the number on the label and the tracking page
    account: str                   # the key's account
    service: Service
    sender: Address
    recipient: Address
    parcel: Parcel
    reference: str = ""            # the sender's own reference, an order number
    status: ShipmentStatus = ShipmentStatus.CREATED
    created_at: datetime = field(default_factory=datetime.utcnow)
    events: list[TrackingEvent] = field(default_factory=list)
    label_url: str = ""            # where the PDF of the label is, once produced; empty before

    def can_cancel(self) -> bool:
        """A sender may cancel until the courier has the parcel."""
        return self.status in (ShipmentStatus.CREATED, ShipmentStatus.LABELLED)


@dataclass
class Subscription:
    id: str                        # WH-<8 hex>
    account: str
    url: str                       # https only; a plain http address is refused
    events: list[str]              # "shipment.status.changed", "shipment.delivery.attempted"
    secret: str                    # given once at creation, never shown again; signs each delivery
    active: bool = True
    failures: int = 0              # deliveries that failed in a row; at 10 the subscription is paused
