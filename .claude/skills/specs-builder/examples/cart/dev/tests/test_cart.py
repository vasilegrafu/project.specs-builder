"""What the cart promises."""
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from voltline.cart import limits, service
from voltline.cart.errors import BadCode, CartClosed, NoSuchProduct, OutOfStock, TooMany
from voltline.cart.models import CartStatus


@pytest.fixture
def cart():
    service.CARTS.clear()
    return service.cart_for("acct-ana")


def test_adding_twice_raises_the_quantity(cart):
    service.add_line(cart, "volt-65", 2)
    service.add_line(cart, "volt-65", 1)
    assert cart.line("volt-65").qty == 3
    assert cart.count == 3


def test_at_most_five_of_one_product(cart):
    service.add_line(cart, "volt-65", 5)
    with pytest.raises(TooMany):
        service.add_line(cart, "volt-65", 1)


def test_out_of_stock_is_refused(cart):
    with pytest.raises(OutOfStock):
        service.add_line(cart, "zen-12")


def test_more_than_the_stock_is_refused(cart):
    with pytest.raises(OutOfStock, match="only 2"):
        service.add_line(cart, "nomad-13", 3)


def test_an_unknown_product_is_404(cart):
    with pytest.raises(NoSuchProduct):
        service.add_line(cart, "no-such-thing")


def test_zero_removes_the_line(cart):
    service.add_line(cart, "hush-700")
    service.set_quantity(cart, "hush-700", 0)
    assert cart.lines == []


def test_delivery_is_free_from_fifty_euros(cart):
    service.add_line(cart, "volt-65", 1)
    assert service.totals(cart)["delivery"] == Decimal("4.90")
    service.add_line(cart, "volt-65", 1)
    assert service.totals(cart)["delivery"] == Decimal("0")


def test_a_code_takes_its_percent_off_the_subtotal(cart):
    service.add_line(cart, "hush-700")
    service.apply_code(cart, "welcome10")
    sums = service.totals(cart)
    assert sums["discount"] == Decimal("29.90")
    assert sums["total"] == Decimal("269.10")


def test_an_unknown_or_expired_code_is_refused(cart):
    with pytest.raises(BadCode, match="not known"):
        service.apply_code(cart, "NOPE1")
    with pytest.raises(BadCode, match="letters and digits"):
        service.apply_code(cart, "no spaces")


def test_a_checked_out_cart_changes_no_more(cart):
    service.add_line(cart, "hush-700")
    service.checkout(cart)
    assert cart.status == CartStatus.CHECKED_OUT
    with pytest.raises(CartClosed):
        service.add_line(cart, "volt-65")


def test_the_visitors_cart_joins_the_accounts_at_sign_in():
    service.CARTS.clear()
    visitor = service.cart_for("s_visitor")
    service.add_line(visitor, "volt-65", 3)
    account = service.cart_for("acct-ana")
    service.add_line(account, "volt-65", 1)
    service.add_line(account, "hush-700", 1)
    service.merge(visitor, account)
    assert account.line("volt-65").qty == 3
    assert len(account.lines) == 2
    assert visitor.status == CartStatus.ABANDONED


def test_stale_carts_are_abandoned_after_thirty_days(cart):
    service.add_line(cart, "volt-65")
    cart.updated_at = datetime.utcnow() - timedelta(days=limits.KEPT_FOR_DAYS + 1)
    assert service.abandon_stale() == 1
    assert cart.status == CartStatus.ABANDONED


@pytest.mark.skip(reason="the price-changed flag needs the catalogue's price history, which the demo has none of")
def test_a_line_shows_that_its_price_changed_since_it_was_added(cart):
    pass
