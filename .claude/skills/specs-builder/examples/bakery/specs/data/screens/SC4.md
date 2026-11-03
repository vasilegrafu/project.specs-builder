---
id: SC4
name: Order placed
kind: page
address: /order/{number}
who: the customer who placed the order
reached by: Place order on SC3
shows: R6
follows: FD11, FD12, FD13, FD14, FD15, FD16, FD18, FD19, FD20
---

A customer sees that their order is placed, with its number and where to collect it.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The order: its number, cake, size, pick-up day, name and price. | R6 | N2 |
| Where to collect it. | R6 | N3 |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Site header, C1 | region | The row every screen starts with; each thing in it is a part of C1. |  | the header | C1 |  |  |  |  |
| 2 | A picture of a cake box | image | A picture of a cake box. |  | a picture of a cake box |  |  | FD16 |  |  |
| 3 | The title | heading | Says the order is placed. |  | the title, as it reads |  | R6 |  |  |  |
| 4 | The order number | text | ML-1043, what the customer quotes. |  | your order number, and the number |  | R6 | N2 |  |  |
| 7 | The order's facts | text | The cake and size, the pick-up day, the name, the price to pay at pick-up and where to collect it. One line each. |  | each fact, as it reads |  | R6 | N2, D7 |  |  |
| 8 | To change or cancel | text | Says to ring the bakery, quoting the number. |  | the line |  | R6 | D7 |  |  |
| 12 | Site footer, C2 | region | The row every screen ends with; each thing in it is a part of C2. |  | the footer | C2 | R8 |  |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| empty | stated | Opened with no order just placed, it leads to SC3. |  |  |
| loading | n/a | It shows what was just recorded, with nothing to wait for. |  |  |
| error | n/a | An order that cannot be recorded stays on SC3. |  |  |
| hover | stated | A link deepens; a touch screen has nothing in its place. |  |  |
| keyboard | stated | Tab reaches the phone number, then the footer; the focus always shows. |  |  |
| mobile | stated | At 375 pixels the facts stand one above another, each name over its value. |  |  |
| navigation | stated | A reload shows the same order and places nothing; back returns to an empty form. |  |  |
| permissions | stated | Only the customer who has just placed it sees it; no one else has a way to it. |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| empty | opened with no order | SC3 | SC3 | R6 |  |
