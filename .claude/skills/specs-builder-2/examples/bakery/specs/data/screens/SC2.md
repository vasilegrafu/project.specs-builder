---
id: SC2
name: What we bake
kind: list
address: /what-we-bake
who: anyone
reached by: What we bake in the header; See what we bake and See everything we bake on SC1
shows: R1
---

A customer looks through what the bakery bakes, with its prices, and chooses a cake to order.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| Each product's name, picture and price, and whether it is a cake. | R1 | N1 |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Site header, C1 | region | The row every screen starts with; each thing in it is a part of C1. |  | the header | C1 |  |  |  |  |
| 2 | The title | heading | What we bake. |  | What we bake |  | R1 |  |  |  |
| 4 | Cakes to order | heading | The heading over the cakes. |  | Cakes to order |  | R1 | B3 |  |  |
| 6 | A product card, C3 | region | One thing the bakery bakes; each thing in it is a part of C3. The rest repeat. |  | the product | C3 | R1 |  |  |  |
| 7 | Also from our oven | heading | The heading over everything that is not a cake. |  | Also from our oven |  | R1 | B3 |  |  |
| 13 | Site footer, C2 | region | The row every screen ends with; each thing in it is a part of C2. |  | the footer | C2 | R8 |  |  |  |
| 14 | The line | text | Says to choose a cake, and that everything else is in the shop. |  | the line |  |  | B3 |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| empty | n/a | The list comes with the page, so there is always something on it. |  |  |
| loading | n/a | The list comes with the page, so nothing waits. |  |  |
| error | n/a | The list comes with the page, so nothing can fail to arrive. |  |  |
| no-results | n/a | The list is not searched or filtered. |  |  |
| hover | stated | A card lifts and its button deepens; a touch screen has nothing in its place. |  |  |
| keyboard | stated | Tab reaches each Order this cake in turn, and the focus always shows; Enter opens the form. |  |  |
| mobile | stated | At 375 pixels the cards stand one above another, the picture on top. |  |  |
| navigation | stated | The address opens it as it is; back from Order a cake returns here. |  |  |
| permissions | stated | Everyone sees the same. |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Order this cake | SC3 | SC3 | R3 |  |
