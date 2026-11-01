"""Placing an order: the orders team's, which calls the cart to close it and the catalogue to take the stock."""
from __future__ import annotations

from voltline.cart import service as cart
from voltline.cart.models import Cart
from voltline.catalogue import service as catalogue
from voltline.orders.models import Order

ORDERS: dict[str, Order] = {}
NEXT = 1048


def place(account_id: str, open_cart: Cart) -> Order:
    """The checkout's Place order. The cart is closed first, so that a refusal leaves it as it was."""
    global NEXT
    closed = cart.checkout(open_cart)
    for line in closed.lines:
        catalogue.take_stock(line.slug, line.qty)
    order = Order(number=f"VL-{NEXT}", account_id=account_id, cart_id=closed.id, total=cart.totals(closed)["total"])
    NEXT += 1
    ORDERS[order.number] = order
    return order
