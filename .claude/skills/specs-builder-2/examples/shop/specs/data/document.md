---
name: Voltline
kind: application, api
status: agreed
---

Voltline is a small electronics shop on the web: a catalogue of six categories, a cart, a checkout with three ways to pay, an account with its orders, and an admin's view of every order.
This specification says what the shop does today, screen by screen and call by call, so that the team moving it to a new platform in the spring of 2027 builds the same shop (E1).

## Problem

The shop is being moved to a new platform and nothing of what the customer sees is to change; without a specification the new team would read the old code and guess.
Today about 12 orders a week are placed by phone because something on the site stopped the customer, most often at the checkout, and 68 of every 100 checkouts started are abandoned, by the shop's own counter in September 2026 (E2, E3).
The owner lays the slowness behind both at the platform's door, and the move is meant to cure it without changing the shop.

## Users

The visitor: anyone who browses the catalogue, searches, and fills a cart without an account (U1).
The customer: a visitor with an account, who buys, sees their orders and keeps their details; today they are stopped by the site about 12 times a week and phone the shop instead (U2).
The admin: the two people in the warehouse, who move each order along from placed to delivered, or cancel it (U3). Each is a customer too, signed in to the same account.

## Journey

1. A visitor arrives at the home page, or at a product from a search engine, and browses a category or searches.
2. They open a product, read its price, its stock and its reviews, and add it to the cart.
3. In the cart they change the quantities, apply a code where they have one, and go to the checkout; signed out, they sign in or create an account first.
4. At the checkout they give the delivery address, choose a way to pay, and place the order; today this is where the site most often stops them, and they phone.
5. Under My orders they follow the order from placed to delivered, and cancel it while it is still placed.
6. In the warehouse the admin marks the order paid, shipped and delivered, with a note where one is needed.

## Non-goals

- A wishlist, reviews written on the site, and gift cards: the owner says no to each every year, and the move is not the moment (E4).
- Anything the shop does not do today: the move adds nothing and loses nothing (E1).
- The warehouse's own tools beyond the admin's orders: the shop ends at the order's status.

## Assumptions

- The shop's counter of abandoned checkouts counts the same thing on the new platform. To check: run both counters on the same week before the old shop is switched off, and compare.
- The orders placed by phone are counted by the warehouse, by hand, and will go on being counted the same way. To check: ask Lea for the count of the first week after launch.

## Release plan

| Release | Holds | Outcome |
|---|---|---|
| First | R1, R2, R3, R4, R5, R6, R7, R8, R9, R10, R11, R12, R13, R14 | the shop as it runs today, on the new platform: a visitor buys, a customer follows the order, the admin moves it |
| Later | R16 | an address the shop does not have gets a page of the shop's own |
