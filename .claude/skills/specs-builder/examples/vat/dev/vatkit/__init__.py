"""vatkit: the VAT of a sale in the EU, and the money it is written in.

    from vatkit import rate_for, vat_of, gross, net, money, check_vat_number

Every function takes and gives Decimal, never float: a cent is never lost to binary. Rates are the standard ones
of each member state as of 1 January 2026, in RATES; a reduced rate is asked for by its category.
"""
from .errors import UnknownCountry, UnknownCategory, BadAmount, BadVatNumber
from .rates import RATES, REDUCED, rate_for
from .compute import vat_of, gross, net, split
from .money import money, round_cents
from .numbers import check_vat_number

__all__ = ["RATES", "REDUCED", "rate_for", "vat_of", "gross", "net", "split", "money", "round_cents",
           "check_vat_number", "UnknownCountry", "UnknownCategory", "BadAmount", "BadVatNumber"]
__version__ = "2.3.0"
