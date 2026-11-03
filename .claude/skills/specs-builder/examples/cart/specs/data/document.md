---
name: Voltline cart
kind: part, api
status: agreed
---

The cart is the part of Voltline's back end that holds what a visitor or a customer has chosen to buy and not yet ordered: its lines, a discount code, and the totals the pages and the checkout show.
This specification says what the cart does today, where it ends, and what it must never do, so that the cart can leave the shop's one service in January 2027 for a service of its own, owned by a new cart team, without breaking anything that calls it (E1).
It is read from the code, its tests and the lead engineer's brief.

## Problem

The cart is being split out of the shop's one service, and nothing says today what the catalogue, accounts and orders teams can count on from it, or what the cart team may not touch (E1).
Two things already go wrong, by the lead engineer's counts of September 2026: about 9 customers a week tell support that their cart was empty, or not what they had put in, after they signed in (E2); and 31 of every 100 codes typed into the cart's code box are refused, most for a space inside or a date passed (E3).
The code shows what a customer meets at that moment: the visitor's lines join whatever the account's cart already held, kept up to thirty days, and of a product in both the larger quantity wins (E60, E68).
Two of the cart's own limits are not held today: a visitor's cart is meant to live 48 hours and nothing holds it to that (X1), and a carried cart can pass thirty products (X3).

## Users

The cart has no screen of its own: people meet it through the shop's pages, and three parts of the back end call it (E5).
The visitor: anyone on the shop without signing in, whose cart is kept by their session (U1).
The customer: a visitor signed in, whose cart is kept by their account and follows them from one session to the next (U2).
Accounts: the part that signs a visitor in, and carries their cart into the account's at that moment (U3).
Orders: the part that places an order from a cart, closes the cart and reads its total (U4).
The nightly job: what lets go, once a night, of the carts nobody has touched (U5).

## Journey

1. A visitor adds products to the cart from the shop's pages; each call answers the whole cart, with its lines and totals.
2. They change a quantity, take a product out, and type a code into the code box; today 31 codes of 100 are refused here.
3. At the checkout they sign in; accounts carries the visitor's cart into the account's; today about 9 customers a week find it empty or changed here.
4. Orders places the order: it closes the cart, which is kept as the order's record, and reads the total.
5. A cart nobody touches is let go by the nightly job.

## Non-goals

- A cart saved for later, or shared with someone else: not now, says the brief (E6).
- Codes that stack: one code at a time, B4, stays as it is (E6, E7).
- A code that may be used once per customer, R11: the marketing team's table does not know who used a code (E12).
- The stock: the cart reads it and never changes it; taking stock is the catalogue's, at orders' call (E84).
- How the split is built: this specification says what the cart answers, not how it is moved.

## Assumptions

- Support's count of carts lost at sign-in counts the same after the split. To check: count the first two weeks of January with the same tag as September.
- The cart's counter of refused codes counts each code typed once, whether refused or applied. To check: compare a day's count with the calls to A5 that day.

## Boundary

The cart is a part of the shop's back end, and this is its edge: what crosses it, both ways, and what stays on the other side.

| What | Is |
|---|---|
| The whole | Voltline's back end: one service with a package per part, each its team's, mounted by platform under /api/v1 (E18, E76); the cart leaves it for a service of its own in January 2027 (E1) |
| Comes in | the shop's pages' calls to the five routes under /api/v1/cart, with the session cookie, A1 to A5 (E22, E76); accounts' call at sign-in, A6 and A9 (E80); orders' calls at checkout, A7 and A10 (E89, E91); the nightly job's call, A8 (E68) |
| Goes out | the cart as the pages read it: its lines with the price when added and the price now, the count, the discount, the subtotal, delivery and total, and the sum from which delivery is free (E21); a closed cart, whose lines and totals are the order's record (E88) |
| Called by | the shop's pages, for the visitor and the customer; accounts, at sign-in; orders, at checkout; the nightly job (E5) |
| Calls | the catalogue, for a product by its slug: its name, its price and its stock (E83); accounts, for the caller's session, which says whose cart it is (E22); the marketing team's codes, read (E56) |
| Never | changes stock: the catalogue takes it, when orders asks (E66, E84); places an order: orders does (E17, E89); signs anyone in or makes a session: accounts does (E16, E79); writes a code: the codes are the marketing team's (E7, E56) |
| Owns | N1 the cart, N2 its lines, N3 its discount (E19, E71) |
| Refers to | N4 the product, owned by the catalogue team; N5 the customer, owned by the accounts team; N6 the order, owned by the orders team; each by its key alone (E15, E16, E17) |

## Release plan

| Release | Holds | Outcome |
|---|---|---|
| First | R1, R2, R3, R4, R5, R6, R7, R8, R9 | the cart as its own service: the pages fill it, accounts carries it at sign-in, orders closes it, the nightly job lets old carts go |
| Later | R10 | a line says when its price changed since it was added |
