---
id: SC5
name: The cart
kind: list
address: /cart
who: anyone: a visitor's cart is kept in the session, a customer's under the account (Q1)
reached by: the cart in the header, on every screen; Add to cart on SC3
displays: N2.empty, N2.open
follows: FD1, FD2, FD3, FD4, FD5, FD6, FD7, FD8, FD9, FD10
---

A visitor or a customer sees what they have chosen, changes it, and goes to the checkout.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The cart's lines, each with the product, its price, the quantity and the line's total; the code applied; the subtotal, the delivery and the total. | R5 | N2, B2 |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C9 | region | The row every screen starts with: the mark, the search, the account and the cart, then the six categories; each thing in it is a part of C9. |  | the banner | C9 |  | E8, E24 |  |  |
| 2 | The title | heading | Your cart. |  | Your cart |  |  | E21 |  |  |
| 3 | The lines, rows of C10 | table | Item, Price, Quantity, Total, Remove: one row per product; each cell is a part of C10. | not shown when the cart is empty | a table of five columns | C10 | R5 | E21, N2 |  |  |
| 4 | A column's name | text | Item, Price, Quantity, Total, and Remove, heard only. |  | the column's name |  |  | E22, N2 |  |  |
| 5 | The summary | region | The cart's sums, a code, and the way on. | not shown when the cart is empty | Summary |  | R5 | B2, E22 |  |  |
| 6 | Summary | heading | The heading of the summary. |  | Summary |  |  | E22 |  |  |
| 7 | A sum's name | text | Subtotal, Delivery, Total: what the value beside it is. |  | the sum's name |  |  | E22 |  |  |
| 8 | The subtotal | text | The lines' totals, added. |  | Subtotal |  | R5 | E22, N2 |  |  |
| 9 | The delivery | text | Free from €50; €4.90 under. |  | Delivery |  | R5 | B2, E23 |  |  |
| 10 | The total | text | The subtotal, less a code, with the delivery. |  | Total |  | R5 | E22 |  |  |
| 11 | Discount code | field | A code to apply to the cart. |  | Discount code |  | R5 | E22 |  |  |
| 12 | Apply, C2 | button | Applies the code. |  | Apply | C2 | R5 | E22 |  |  |
| 13 | Checkout, C1 | link | Opens the checkout. Leads to SC6. |  | Checkout | C1 | R6 | E22 |  | SC6 |
| 14 | Continue shopping | link | Back to the shop. Leads to SC1. |  | Continue shopping |  |  | E22 |  | SC1 |
| 15 | The empty cart's words | message | Your cart is empty. | when the cart is empty | the message |  | R5 | E20 |  |  |
| 16 | Start shopping, C1 | link | Back to the shop. Leads to SC1. | when the cart is empty | Start shopping | C1 |  | E20 |  | SC1 |
| 17 | The cart follows a customer | text | Signed in? Your cart follows you. With Sign in. Leads to SC7. | when the cart is empty | the line |  |  | E20 |  | SC7 |
| 18 | The footer, C13 | region | The row every screen ends with: the shop's line, its four pages and the fine print; each thing in it is a part of C13. |  | the footer | C13 |  | E8 |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Empty | observed | The empty cart's words in place of the lines and the summary. | E20 |  |
| Loading | n/a | The page arrives whole from the server; nothing on it waits for a call. |  |  |
| Error | likely |  |  | Open /cart on a copy of the shop with the cart's server stopped. |
| No-results | n/a | The cart is neither searched nor filtered. |  |  |
| Hover | observed | A line's minus and plus take a grey ground under the pointer; Checkout darkens, C1. | E48 |  |
| Keyboard | observed | Tab reaches each line's product, minus, quantity, plus and Remove, then the code, Apply, Checkout and Continue shopping; the focus shows on each. | E46 |  |
| Mobile | observed | At 375 pixels each line is a block of its own, and the summary stands under the lines. Seen in evidence/captures/site/shots/V21-375.jpg. |  |  |
| Navigation | likely |  |  | Change a quantity, reload the cart, and see whether the change stays. |
| Permissions | observed | Signed out, the cart is the visitor's own and empty at first; signed in, it is the account's. | E20 |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | A line's plus or minus is selected | normal |  | R5 | E21 |
| normal | The last line's minus at 1, or its Remove, is selected | empty |  | R5 | E21 |
| normal | Checkout is selected | SC6 | SC6 | R6 | E22 |
| empty | Start shopping is selected | SC1 | SC1 | R5 | E20 |
| normal | Sign out, in the header's menu | SC10 | SC10 | R10 | E24 |

## Layout

| What | Must be | From |
|---|---|---|
| The summary | 320 pixels wide, at the right of the lines; under them under 800 pixels | foundations |
