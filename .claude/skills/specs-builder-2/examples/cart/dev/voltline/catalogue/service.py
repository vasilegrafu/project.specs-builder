"""What the catalogue answers to the other parts: a product by its slug, and stock taken for an order."""
from __future__ import annotations

from decimal import Decimal

from voltline.catalogue.models import Product

# A few of the shop's products stand in for the catalogue's table.
PRODUCTS: dict[str, Product] = {p.slug: p for p in [
    Product("aero-14", "Aero 14", "laptops", Decimal("1099.00"), 12, "LT-AER-14", Decimal("1249.00")),
    Product("hush-700", "Hush 700", "audio", Decimal("299.00"), 8, "AU-HSH-700"),
    Product("volt-65", "Volt 65 charger", "accessories", Decimal("39.00"), 40, "AC-VLT-65"),
    Product("nomad-13", "Nomad 13", "laptops", Decimal("749.00"), 2, "LT-NMD-13"),
    Product("zen-12", "Zen 12", "laptops", Decimal("899.00"), 0, "LT-ZEN-12"),
]}


def product(slug: str) -> Product | None:
    return PRODUCTS.get(slug)


def take_stock(slug: str, qty: int) -> None:
    """Orders calls this when an order is placed. Not the cart's to call."""
    item = PRODUCTS[slug]
    if item.stock < qty:
        raise ValueError(f"{slug}: {item.stock} in stock, {qty} wanted")
    item.stock -= qty
