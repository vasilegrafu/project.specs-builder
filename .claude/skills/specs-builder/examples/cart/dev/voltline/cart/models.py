"""The cart and its lines: what the part owns. A product is the catalogue's and is only referred to by its slug."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum


class CartStatus(str, Enum):
    OPEN = "open"                  # the customer is still shopping
    CHECKED_OUT = "checked_out"    # an order was placed from it; it is kept for the order's record and never changed
    ABANDONED = "abandoned"        # untouched past the keeping time; the nightly job marks it and its lines are let go


@dataclass
class Line:
    slug: str                      # the catalogue's product, by its slug; the name and the price are read from there
    qty: int
    unit_price: Decimal            # the price when the line was added; a later price change is shown on the cart page
    added_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def total(self) -> Decimal:
        return self.unit_price * self.qty


@dataclass
class Discount:
    code: str
    percent: int                   # 5 to 50
    applied_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Cart:
    id: str                        # CT-<10 hex>
    owner: str                     # the customer's account id, or the session id of a visitor
    status: CartStatus = CartStatus.OPEN
    lines: list[Line] = field(default_factory=list)
    discount: Discount | None = None
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def line(self, slug: str) -> Line | None:
        return next((line for line in self.lines if line.slug == slug), None)

    @property
    def count(self) -> int:
        """What the header's badge shows: every unit, not every line."""
        return sum(line.qty for line in self.lines)
