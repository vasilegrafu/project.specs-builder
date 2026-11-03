"""The cart's routes: what the shop's pages call. Each is thin: the rules are in service.py."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from voltline.accounts.session import Session, current_session
from voltline.cart import limits, service
from voltline.cart.errors import CartError
from voltline.cart.models import Cart
from voltline.catalogue import service as catalogue

router = APIRouter(prefix="/cart", tags=["cart"])


class AddLine(BaseModel):
    slug: str
    qty: int = Field(default=1, ge=1, le=limits.MAX_QTY_PER_LINE)


class SetQuantity(BaseModel):
    qty: int = Field(ge=0, le=limits.MAX_QTY_PER_LINE)


class ApplyCode(BaseModel):
    code: str = Field(min_length=1, max_length=12)


def cart_out(cart: Cart) -> dict:
    """What every answer holds: the lines with the catalogue's current name and price beside the price when
    added, and the totals."""
    lines = []
    for line in cart.lines:
        product = catalogue.product(line.slug)
        lines.append({"slug": line.slug, "name": product.name if product else line.slug, "qty": line.qty,
                      "unit_price": str(line.unit_price),
                      "price_now": str(product.price) if product else None,
                      "price_changed": bool(product and product.price != line.unit_price),
                      "in_stock": bool(product and product.stock >= line.qty), "total": str(line.total)})
    sums = service.totals(cart)
    return {"id": cart.id, "status": cart.status.value, "count": cart.count, "lines": lines,
            "discount": {"code": cart.discount.code, "percent": cart.discount.percent} if cart.discount else None,
            **{key: str(value) for key, value in sums.items()},
            "free_delivery_over": str(limits.FREE_DELIVERY_OVER)}


def mine(session: Session = Depends(current_session)) -> Cart:
    """The caller's open cart: the account's where signed in, the session's for a visitor."""
    return service.cart_for(session.account_id or session.id)


def refused(problem: CartError) -> HTTPException:
    return HTTPException(status_code=problem.status, detail={"error": problem.message})


@router.get("")
def get_cart(cart: Cart = Depends(mine)) -> dict:
    """The cart as it stands."""
    return cart_out(cart)


@router.post("/lines")
def add_line(body: AddLine, cart: Cart = Depends(mine)) -> dict:
    """Add a product, or raise its quantity."""
    try:
        return cart_out(service.add_line(cart, body.slug, body.qty))
    except CartError as problem:
        raise refused(problem) from problem


@router.patch("/lines/{slug}")
def set_quantity(slug: str, body: SetQuantity, cart: Cart = Depends(mine)) -> dict:
    """Set a line's quantity; 0 removes it."""
    try:
        return cart_out(service.set_quantity(cart, slug, body.qty))
    except CartError as problem:
        raise refused(problem) from problem


@router.delete("/lines/{slug}")
def remove_line(slug: str, cart: Cart = Depends(mine)) -> dict:
    """Take a product out."""
    try:
        return cart_out(service.remove_line(cart, slug))
    except CartError as problem:
        raise refused(problem) from problem


@router.post("/code")
def apply_code(body: ApplyCode, cart: Cart = Depends(mine)) -> dict:
    """Apply a discount code; a second replaces the first."""
    try:
        return cart_out(service.apply_code(cart, body.code))
    except CartError as problem:
        raise refused(problem) from problem
