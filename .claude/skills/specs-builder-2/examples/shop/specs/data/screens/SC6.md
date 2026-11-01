---
id: SC6
name: Checkout
kind: form
address: /checkout
who: a customer, signed in; a visitor is sent to sign in first (R6)
reached by: Checkout on SC5
---

A customer gives the delivery address and the way to pay, and places the order.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The delivery address, from the customer's profile, and the way to pay; the cart's total. | R6 | N3, N4 |
| Place order sends the address, the way to pay and the code to make the order. | R6 |  |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C9 | region | The row every screen starts with: the mark, the search, the account and the cart, then the six categories; each thing in it is a part of C9. |  | the banner | C9 |  | E8, E24 |  |  |
| 2 | The title | heading | Checkout. |  | Checkout |  |  | E25 |  |  |
| 3 | Delivery address | text | The name of the four fields under it. |  | Delivery address |  |  | E25 |  |  |
| 4 | Full name, C7 | field | The full name of the delivery address, required. |  | Full name | C7 | R6 | E25, N4 |  |  |
| 5 | Street and number, C7 | field | The street and number of the delivery address, required. |  | Street and number | C7 | R6 | E25, N4 |  |  |
| 6 | City, C7 | field | The city of the delivery address, required. |  | City | C7 | R6 | E25, N4 |  |  |
| 7 | Postcode, C7 | field | The postcode of the delivery address, required. |  | Postcode | C7 | R6 | E25, N4 |  |  |
| 8 | A way to pay | field | Card, PayPal or Invoice, one of three; Card chosen to start. |  | the way to pay |  | R6 | E25 |  |  |
| 9 | Payment | text | The name of the ways to pay under it. |  | Payment |  |  | E25 |  |  |
| 10 | The total | text | Total €377.00: the cart's total. |  | the total |  | R6 | E25 |  |  |
| 11 | Place order, C1 | button | Places the order from the cart. |  | Place order | C1 | R6 | B5 |  |  |
| 12 | Back to cart | link | Back to the cart. Leads to SC5. |  | Back to cart |  |  | E25 |  | SC5 |
| 13 | The footer, C13 | region | The row every screen ends with: the shop's line, its four pages and the fine print; each thing in it is a part of C13. |  | the footer | C13 |  | E8 |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Empty | likely |  |  | Check out as a customer whose profile has no address, on a copy of the shop. |
| Validation | likely |  |  | Empty Street and number and select Place order, on a copy of the shop. |
| Error | likely |  |  | Place an order with the network cut, on a copy of the shop. |
| Loading | likely |  |  | Place an order with the network slowed, on a copy of the shop. |
| Success | likely |  |  | Place an order on a copy of the shop: Place order was a stop point of the walk. |
| Disabled | n/a | Place order is always enabled: what is missing is said when it is selected (R6). |  |  |
| Unauthorized | likely |  |  | Open /checkout signed out. |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Place order, the address filled | success |  | R6 | E25 |
| normal | Back to cart is selected | SC5 | SC5 | R5 | E25 |
