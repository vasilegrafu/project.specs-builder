"""VAT numbers: whether one is in the form its country gives it. Whether it is registered is the VIES service's to
say, which vatkit never calls: it has no network."""
from __future__ import annotations

import re

from .errors import BadVatNumber
from .rates import country_of

FORMS = {
    "DE": r"\d{9}", "AT": r"U\d{8}", "FR": r"[0-9A-HJ-NP-Z]{2}\d{9}", "NL": r"\d{9}B\d{2}", "BE": r"[01]\d{9}",
    "IT": r"\d{11}", "ES": r"[0-9A-Z]\d{7}[0-9A-Z]", "PL": r"\d{10}", "GR": r"\d{9}", "IE": r"\d{7}[A-W][A-I]?",
}


def check_vat_number(number: str) -> str:
    """The number written as it is filed -- its two letters, then the rest, no spaces or dots -- where its form is
    right for its country; BadVatNumber where it is not. A country with no form here is taken on its two letters."""
    said = re.sub(r"[\s.\-]", "", number or "").upper()
    if len(said) < 4:
        raise BadVatNumber(f"{number!r} is too short to be a VAT number")
    code = country_of(said[:2])
    rest = said[2:]
    form = FORMS.get(code)
    if form and not re.fullmatch(form, rest):
        raise BadVatNumber(f"{said} is not in the form of a {code} VAT number")
    return said[:2] + rest
