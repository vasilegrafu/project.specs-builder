"""The catalogue's things. Owned by the catalogue team; the cart reads them and never writes them."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class Availability(str, Enum):
    IN_STOCK = "in"
    LOW = "low"                    # three or fewer
    OUT = "out"


@dataclass
class Product:
    slug: str
    name: str
    category: str
    price: Decimal
    stock: int
    sku: str
    old_price: Decimal | None = None

    @property
    def availability(self) -> Availability:
        if self.stock <= 0:
            return Availability.OUT
        return Availability.LOW if self.stock <= 3 else Availability.IN_STOCK
