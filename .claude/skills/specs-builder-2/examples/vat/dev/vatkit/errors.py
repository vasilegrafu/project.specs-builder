"""What vatkit refuses. Each is a ValueError, so a caller that catches that catches them all."""


class UnknownCountry(ValueError):
    """A country that is not a member state, or not written as its two letters: DE, FR, NL."""


class UnknownCategory(ValueError):
    """A category of goods with no reduced rate in that country."""


class BadAmount(ValueError):
    """An amount that is not a Decimal, a whole number or a string of one; or is below zero."""


class BadVatNumber(ValueError):
    """A VAT number out of the form its country gives it."""
