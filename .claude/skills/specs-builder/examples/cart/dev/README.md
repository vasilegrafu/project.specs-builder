# Voltline's back end, and the cart in it

The code behind the Voltline shop (`../../shop/`): one Python service,
`voltline/`, with a package per part. **The cart, `voltline/cart/`, is
the part to specify**; the rest is the whole it lives in, here so that
the cart's edges can be read -- what calls it, what it calls, what it
owns and what it only reads.

| Package | Is | Owner |
|---|---|---|
| `voltline/cart/` | the cart: its lines, their quantities, the discount code, the totals; what the shop's pages and the checkout call | **the part specified here** |
| `voltline/catalogue/` | the products and their stock | the catalogue team |
| `voltline/accounts/` | customers, sessions, who is the admin | the accounts team |
| `voltline/orders/` | an order, placed from a cart, and its life | the orders team |
| `voltline/web/` | the HTTP app that mounts every part's routes | platform |

Run the tests with `pytest`; `voltline/web/app.py` is what `uvicorn`
serves. Demo material for the specs-builder skill: nothing here talks to
a real database or a real shop.
