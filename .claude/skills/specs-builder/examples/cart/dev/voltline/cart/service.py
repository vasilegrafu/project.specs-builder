"""What the cart does: add, change, remove, apply a code, total. Every rule of the cart is enforced here, once,
whichever route or part calls it. The catalogue is asked for products and stock; nothing of it is kept."""
from __future__ import annotations

import re
import secrets
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

from voltline.catalogue import service as catalogue
from voltline.cart import limits
from voltline.cart.errors import BadCode, CartClosed, NoSuchProduct, OutOfStock, TooMany
from voltline.cart.models import Cart, CartStatus, Discount, Line

CARTS: dict[str, Cart] = {}        # stands in for the carts table

# The codes the shop runs; in the product they are the marketing team's table, read, never written here.
CODES = {"WELCOME10": (10, datetime(2027, 1, 1)), "AUTUMN5": (5, datetime(2026, 11, 30)),
         "STAFF20": (20, datetime(2026, 12, 31))}


def cart_for(owner: str) -> Cart:
    """The owner's open cart, made where there is none. A visitor's cart is carried to their account at sign-in
    by accounts, which calls merge()."""
    for cart in CARTS.values():
        if cart.owner == owner and cart.status == CartStatus.OPEN:
            return cart
    cart = Cart(id="CT-" + secrets.token_hex(5), owner=owner)
    CARTS[cart.id] = cart
    return cart


def _open(cart: Cart) -> None:
    if cart.status != CartStatus.OPEN:
        raise CartClosed("this cart has been checked out; start a new one")


def add_line(cart: Cart, slug: str, qty: int = 1) -> Cart:
    """Add a product, or raise its quantity where it is in the cart already. Refused: a product that is not in the
    catalogue, out of stock, or asked for beyond the stock or the limit per line."""
    _open(cart)
    product = catalogue.product(slug)
    if product is None:
        raise NoSuchProduct("no product has that slug")
    if product.stock == 0:
        raise OutOfStock(f"{product.name} is out of stock")
    line = cart.line(slug)
    wanted = (line.qty if line else 0) + qty
    if wanted > limits.MAX_QTY_PER_LINE:
        raise TooMany(f"up to {limits.MAX_QTY_PER_LINE} of each product")
    if wanted > product.stock:
        raise OutOfStock(f"only {product.stock} of {product.name} left")
    if line is None:
        if len(cart.lines) >= limits.MAX_LINES:
            raise TooMany(f"a cart holds up to {limits.MAX_LINES} different products")
        cart.lines.append(Line(slug=slug, qty=qty, unit_price=product.price))
    else:
        line.qty = wanted
    cart.updated_at = datetime.utcnow()
    return cart


def set_quantity(cart: Cart, slug: str, qty: int) -> Cart:
    """Set a line's quantity; zero removes the line, as the page's minus at one does."""
    _open(cart)
    line = cart.line(slug)
    if line is None:
        raise NoSuchProduct("that product is not in the cart")
    if qty <= 0:
        return remove_line(cart, slug)
    product = catalogue.product(slug)
    if qty > limits.MAX_QTY_PER_LINE:
        raise TooMany(f"up to {limits.MAX_QTY_PER_LINE} of each product")
    if product is not None and qty > product.stock:
        raise OutOfStock(f"only {product.stock} of {product.name} left")
    line.qty = qty
    cart.updated_at = datetime.utcnow()
    return cart


def remove_line(cart: Cart, slug: str) -> Cart:
    _open(cart)
    cart.lines = [line for line in cart.lines if line.slug != slug]
    cart.updated_at = datetime.utcnow()
    return cart


def apply_code(cart: Cart, code: str) -> Cart:
    """One code per cart; a second replaces the first. Not known, expired, or out of form: refused, and the page
    says so under the field."""
    _open(cart)
    code = code.strip().upper()
    if not re.match(limits.CODE_PATTERN, code):
        raise BadCode("a code is 4 to 12 letters and digits")
    known = CODES.get(code)
    if known is None:
        raise BadCode("that code is not known")
    percent, until = known
    if datetime.utcnow() > until:
        raise BadCode(f"{code} expired on {until:%d %B %Y}")
    cart.discount = Discount(code=code, percent=percent)
    cart.updated_at = datetime.utcnow()
    return cart


def totals(cart: Cart) -> dict[str, Decimal]:
    """Subtotal, discount, delivery, total: the numbers the cart page and the checkout show, computed here alone."""
    subtotal = sum((line.total for line in cart.lines), Decimal("0"))
    discount = (subtotal * cart.discount.percent / 100).quantize(Decimal("0.01"), ROUND_HALF_UP) \
        if cart.discount else Decimal("0")
    after = subtotal - discount
    delivery = Decimal("0") if after >= Decimal(str(limits.FREE_DELIVERY_OVER)) or not cart.lines \
        else Decimal(str(limits.DELIVERY))
    return {"subtotal": subtotal, "discount": discount, "delivery": delivery, "total": after + delivery}


def merge(visitor_cart: Cart, account_cart: Cart) -> Cart:
    """At sign-in, what the visitor put in the cart joins the account's: the larger quantity of a product wins,
    within the limit. Called by accounts; the visitor's cart is then abandoned."""
    for line in visitor_cart.lines:
        mine = account_cart.line(line.slug)
        if mine is None:
            account_cart.lines.append(line)
        else:
            mine.qty = min(max(mine.qty, line.qty), limits.MAX_QTY_PER_LINE)
    visitor_cart.status = CartStatus.ABANDONED
    account_cart.updated_at = datetime.utcnow()
    return account_cart


def checkout(cart: Cart) -> Cart:
    """Called by orders once the order is placed: the cart closes and is the order's record. Stock is the
    catalogue's to take; the cart never changes stock."""
    _open(cart)
    if not cart.lines:
        raise OutOfStock("the cart is empty")
    for line in cart.lines:
        product = catalogue.product(line.slug)
        if product is None or product.stock < line.qty:
            raise OutOfStock(f"{line.slug} is no longer in stock in that quantity")
    cart.status = CartStatus.CHECKED_OUT
    cart.updated_at = datetime.utcnow()
    return cart


def abandon_stale(now: datetime | None = None) -> int:
    """The nightly job: open carts untouched for KEPT_FOR_DAYS are marked abandoned. Returns how many."""
    now = now or datetime.utcnow()
    stale = [c for c in CARTS.values() if c.status == CartStatus.OPEN
             and now - c.updated_at > timedelta(days=limits.KEPT_FOR_DAYS)]
    for cart in stale:
        cart.status = CartStatus.ABANDONED
    return len(stale)
