"""What vatkit promises."""
from decimal import Decimal

import pytest

from vatkit import (BadAmount, BadVatNumber, UnknownCategory, UnknownCountry, check_vat_number, gross, money, net,
                    rate_for, split, vat_of)


def test_the_standard_rate_of_a_country():
    assert rate_for("DE") == Decimal("0.19")
    assert rate_for("fr") == Decimal("0.20")


def test_greece_is_taken_as_el_and_as_gr():
    assert rate_for("EL") == rate_for("GR") == Decimal("0.24")


def test_a_country_outside_the_eu_is_refused():
    with pytest.raises(UnknownCountry):
        rate_for("CH")


def test_a_reduced_rate_by_its_category():
    assert rate_for("DE", "books") == Decimal("0.07")


def test_a_category_with_no_reduced_rate_is_refused_never_charged_standard():
    with pytest.raises(UnknownCategory):
        rate_for("DK", "books")


def test_vat_on_a_net_price_to_the_cent():
    assert vat_of("100.00", "DE") == Decimal("19.00")
    assert vat_of("0.05", "DE") == Decimal("0.01")          # 0.0095, half up


def test_net_and_vat_make_the_gross_to_the_cent():
    for price in ("119.00", "0.99", "1234.57"):
        assert net(price, "DE") + vat_of(net(price, "DE"), "DE") in (Decimal(price), Decimal(price) - Decimal("0.01"),
                                                                       Decimal(price) + Decimal("0.01"))


def test_gross_from_net():
    assert gross("100", "FR") == Decimal("120.00")


def test_a_float_is_refused():
    with pytest.raises(BadAmount, match="never a float"):
        vat_of(0.1, "DE")


def test_an_amount_below_zero_is_refused():
    with pytest.raises(BadAmount, match="below zero"):
        vat_of("-1", "DE")


def test_a_sale_is_split_by_rate_and_taxed_once_per_rate():
    done = split([("10.00", None), ("10.00", None), ("20.00", "books")], "DE")
    assert done["19%"] == {"net": Decimal("20.00"), "vat": Decimal("3.80"), "gross": Decimal("23.80")}
    assert done["7%"]["vat"] == Decimal("1.40")


def test_money_as_each_country_writes_it():
    assert money("1234.5", "DE") == "1.234,50 €"
    assert money("1234.5", "IE") == "€1,234.50"
    assert money("1234.5") == "€1,234.50"


def test_a_vat_number_in_its_form():
    assert check_vat_number("de 123 456 789") == "DE123456789"
    with pytest.raises(BadVatNumber):
        check_vat_number("DE12345")


@pytest.mark.skip(reason="the 2026 rates of Finland and Romania changed mid-year; the table follows on release")
def test_a_rate_that_changed_during_the_year():
    pass
