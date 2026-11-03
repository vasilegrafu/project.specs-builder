"""The VAT of a sale: from the net price, from the gross price, and a sale of many lines split by rate."""
from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal

from .money import amount, round_cents
from .rates import rate_for


def vat_of(net_price: object, country: str, category: str | None = None) -> Decimal:
    """The VAT on a net price, to the cent: vat_of("100.00", "DE") is 19.00."""
    return round_cents(amount(net_price) * rate_for(country, category))


def gross(net_price: object, country: str, category: str | None = None) -> Decimal:
    """The price with its VAT: the net, plus vat_of, each to the cent first."""
    return round_cents(net_price) + vat_of(net_price, country, category)


def net(gross_price: object, country: str, category: str | None = None) -> Decimal:
    """The price without its VAT, from a gross price: net("119.00", "DE") is 100.00. The VAT is what is left, so
    net + VAT is the gross to the cent, always."""
    whole = round_cents(gross_price)
    return round_cents(whole / (1 + rate_for(country, category)))


def split(lines: Iterable[tuple[object, str | None]], country: str) -> dict[str, dict[str, Decimal]]:
    """A sale of many lines, each a net price and its category or None, as an invoice must show it: per rate, the
    net, the VAT and the gross. The VAT is computed once per rate on the sum of its lines, never line by line, so
    that the invoice's VAT is what the tax office computes."""
    by_rate: dict[Decimal, Decimal] = {}
    for price, category in lines:
        rate = rate_for(country, category)
        by_rate[rate] = by_rate.get(rate, Decimal("0")) + round_cents(price)
    out = {}
    for rate, total in sorted(by_rate.items(), reverse=True):
        vat = round_cents(total * rate)
        out[f"{(rate * 100).normalize():f}%"] = {"net": total, "vat": vat, "gross": total + vat}
    return out
