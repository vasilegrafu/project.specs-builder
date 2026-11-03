"""An order and its life. Owned by the orders team; an order is placed from a cart and keeps the cart's id."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum


class OrderStatus(str, Enum):
    PLACED = "placed"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class Order:
    number: str                    # VL-<4 digits>
    account_id: str
    cart_id: str                   # the checked-out cart: its lines and totals are the order's record
    total: Decimal
    status: OrderStatus = OrderStatus.PLACED
    placed_at: datetime = field(default_factory=datetime.utcnow)
