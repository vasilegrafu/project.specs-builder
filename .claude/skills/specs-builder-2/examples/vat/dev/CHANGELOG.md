# Changelog

## 2.3.0, 2026-01-12

- Finland's standard rate is 25.5%, from 1 January 2026.
- `split()` names each rate as it is written on an invoice: `"25.5%"`.

## 2.2.0, 2025-07-02

- `check_vat_number()` takes EL for Greece as well as GR.
- `money()` writes France's thousands with a narrow space.

## 2.0.0, 2025-01-08

- Every function takes and gives `Decimal`; a float is refused. Before, a float was taken and rounded, and a cent
  went missing on one invoice in a few thousand.
- `split()` computes the VAT once per rate on the sum of its lines. Before, it was computed line by line, and an
  invoice of many small lines could differ from the tax office's figure by a few cents.

## 1.4.0, 2024-06-20

- Reduced rates for books and food in DE, FR, NL, AT and IT, asked for by their category.
