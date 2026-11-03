"""The rates: the standard rate of each member state, and the reduced rates of the categories that have one.

Rates change by law, a few a year; a release of vatkit follows each within a month, and AS_OF says which day the
table holds. A rate is a Decimal fraction: 0.19 is 19%.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from .errors import UnknownCategory, UnknownCountry

AS_OF = date(2026, 1, 1)

RATES: dict[str, Decimal] = {
    "AT": Decimal("0.20"), "BE": Decimal("0.21"), "BG": Decimal("0.20"), "CY": Decimal("0.19"),
    "CZ": Decimal("0.21"), "DE": Decimal("0.19"), "DK": Decimal("0.25"), "EE": Decimal("0.24"),
    "ES": Decimal("0.21"), "FI": Decimal("0.255"), "FR": Decimal("0.20"), "GR": Decimal("0.24"),
    "HR": Decimal("0.25"), "HU": Decimal("0.27"), "IE": Decimal("0.23"), "IT": Decimal("0.22"),
    "LT": Decimal("0.21"), "LU": Decimal("0.17"), "LV": Decimal("0.21"), "MT": Decimal("0.18"),
    "NL": Decimal("0.21"), "PL": Decimal("0.23"), "PT": Decimal("0.23"), "RO": Decimal("0.21"),
    "SE": Decimal("0.25"), "SI": Decimal("0.22"), "SK": Decimal("0.23"),
}

# Reduced rates by category, where a country has one. A category a country has no reduced rate for is refused,
# never silently charged at the standard rate: the caller decides.
REDUCED: dict[str, dict[str, Decimal]] = {
    "DE": {"books": Decimal("0.07"), "food": Decimal("0.07")},
    "FR": {"books": Decimal("0.055"), "food": Decimal("0.055"), "medicine": Decimal("0.021")},
    "NL": {"books": Decimal("0.09"), "food": Decimal("0.09")},
    "AT": {"books": Decimal("0.10"), "food": Decimal("0.10")},
    "IT": {"books": Decimal("0.04"), "food": Decimal("0.10")},
}

# Greece writes its two letters EL in a VAT number; ISO writes GR. Both are taken.
ALIASES = {"EL": "GR"}


def country_of(code: str) -> str:
    """The member state, by its two letters in either case; EL is GR."""
    code = (code or "").strip().upper()
    code = ALIASES.get(code, code)
    if code not in RATES:
        raise UnknownCountry(f"{code or 'nothing'} is not a member state of the EU")
    return code


def rate_for(country: str, category: str | None = None) -> Decimal:
    """The rate of a sale in that country: the standard one, or the reduced one of the category."""
    code = country_of(country)
    if category is None:
        return RATES[code]
    reduced = REDUCED.get(code, {})
    if category not in reduced:
        raise UnknownCategory(f"{code} has no reduced rate for {category}")
    return reduced[category]
