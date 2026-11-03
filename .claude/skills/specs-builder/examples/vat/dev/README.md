# vatkit

A small Python library for the VAT of a sale in the EU: the rate of each
member state and its reduced rates by category, the VAT on a net price,
the net in a gross price, a sale of many lines split by rate as an invoice
must show it, money written as each country writes it, and whether a VAT
number is in its country's form. Used by the Voltline shop's invoices
and by its back office; published on the company's package index.

```
pip install vatkit
```

```python
from vatkit import vat_of, gross, net, split, money, check_vat_number

vat_of("100.00", "DE")                 # Decimal('19.00')
gross("100", "FR")                     # Decimal('120.00')
net("119.00", "DE")                    # Decimal('100.00')
split([("10", None), ("20", "books")], "DE")
money("1234.5", "DE")                  # '1.234,50 €'
check_vat_number("de 123 456 789")     # 'DE123456789'
```

And from the shell: `vatkit gross 100 DE`, `vatkit rate DE --category books`,
`vatkit check DE123456789`.

## What it promises

- Every amount is a `Decimal`, given and taken; a float is refused, since
  0.1 is not a tenth in binary.
- Every result is to the cent, rounded half up, as the tax offices round.
- A sale's VAT is computed once per rate on the sum of its lines, never
  line by line.
- A category with no reduced rate in a country is refused, never charged
  at the standard rate behind the caller's back.
- No network: whether a VAT number is registered is the VIES service's to
  say, and vatkit never calls it.

## Versions

The rates are those in force on `vatkit.rates.AS_OF`. A release follows
each change of a rate within a month; the major version changes only when
a function's name or what it takes changes.

## Files

- `vatkit/`: the library, a module each: the rates, the computing, money, VAT numbers, the errors, the command line.
- `tests/`: what it promises.
- `CHANGELOG.md`: what changed in each release.

Demo material for the specs-builder skill.
