"""What the cart refuses, each with the words the page shows."""


class CartError(Exception):
    status = 409

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NoSuchProduct(CartError):
    status = 404


class OutOfStock(CartError):
    """The product has no stock, or less than the quantity asked for."""


class TooMany(CartError):
    """More than MAX_QTY_PER_LINE of one product, or more than MAX_LINES products."""


class BadCode(CartError):
    """A discount code that is not known, expired, or already used by this customer."""
    status = 422


class CartClosed(CartError):
    """The cart has been checked out: it is the order's record now and changes no more."""
