"""Money: amounts to the cent, rounded half up, and written as each country writes them."""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from .errors import BadAmount

CENT = Decimal("0.01")

# How an amount is written: the thousands' mark, the decimal mark, and where the euro sign goes.
STYLES = {
    "DE": (".", ",", "after"), "AT": (".", ",", "after"), "NL": (".", ",", "before"), "FR": (" ", ",", "after"),
    "IT": (".", ",", "after"), "ES": (".", ",", "after"), "IE": (",", ".", "before"),
}
DEFAULT_STYLE = (",", ".", "before")      # every other country, and none given: €1,234.50


def amount(value: object) -> Decimal:
    """A Decimal from a Decimal, a whole number or a string. A float is refused: 0.1 is not a tenth."""
    if isinstance(value, bool) or isinstance(value, float):
        raise BadAmount(f"{value!r}: give a Decimal, a whole number or a string, never a float")
    try:
        found = Decimal(value) if not isinstance(value, Decimal) else value
    except (InvalidOperation, TypeError) as problem:
        raise BadAmount(f"{value!r} is not an amount") from problem
    if found < 0:
        raise BadAmount(f"{value!r} is below zero: a refund is a sale of its own, written as a credit")
    return found


def round_cents(value: object) -> Decimal:
    """To the cent, half up: 0.005 is 0.01, as every member state's tax office rounds."""
    return amount(value).quantize(CENT, rounding=ROUND_HALF_UP)


def money(value: object, country: str | None = None) -> str:
    """The amount as the country writes it: money(1234.5, "DE") is '1.234,50 €'; with no country, '€1,234.50'."""
    thousands, decimal, where = STYLES.get((country or "").upper(), DEFAULT_STYLE)
    whole, cents = f"{round_cents(value):,.2f}".split(".")
    said = whole.replace(",", thousands) + decimal + cents
    return f"{said} €" if where == "after" else f"€{said}"
