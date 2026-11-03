---
id: SC1
name: The home page
kind: page
address: /
who: anyone, signed in or not
reached by: the shop's address; the mark in the header, from every screen; Back to the shop on SC10, SC16 and SC18
follows: FD1, FD2, FD3, FD4, FD5, FD6, FD7, FD8, FD9, FD10
---

A visitor sees what the shop has this week and goes into a category, a product or a search.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The week's deal, the six categories, four products with a deal and the four newest, from the catalogue. | R1 | N1 |
| Four popular searches, chosen by the shop. | R3 |  |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C9 | region | The row every screen starts with: the mark, the search, the account and the cart, then the six categories; each thing in it is a part of C9. | signed in: the greeting and its menu in place of Sign in and Sign up | the banner | C9 |  | E8, E24 |  |  |
| 2 | The week's deal | region | The product of the week, with its price and a way to it. |  | the deal |  | R2 | E7 |  |  |
| 3 | The kicker | text | THIS WEEK, over the deal. |  | This week |  |  | E7 |  |  |
| 4 | The deal's name | heading | The product of the week: Aero 16 Pro. |  | Aero 16 Pro |  |  | E7, N1 |  |  |
| 5 | The deal's line | text | What it is, in one line. |  | the line |  |  | E7 |  |  |
| 6 | The deal's price, C4 | text | Its price, the old one struck out, and Deal. |  | the price | C4 |  | B8, E7 |  |  |
| 7 | See the deal, C1 | link | Opens the product. Leads to SC3. |  | See the deal | C1 | R2 |  |  | SC3 |
| 8 | The deal's picture | picture | The product's picture. |  | Aero 16 Pro |  |  | N1 |  |  |
| 9 | Shop by category | heading | The heading over the six tiles. |  | Shop by category |  |  | E7 |  |  |
| 10 | A category's tile | link | A category's picture and name, one of six; opens it. Leads to SC2. |  | the category's name |  | R1 | E7 |  | SC2 |
| 11 | Deals this week | heading | The heading over four products with a deal. |  | Deals this week |  |  | E7 |  |  |
| 12 | The deals, cards of C3 | list | Four products with a deal. Each card's parts are C3's. |  | The deals | C3 | R1 | E7 |  |  |
| 13 | New arrivals | heading | The heading over the four newest products. |  | New arrivals |  |  | E7 |  |  |
| 14 | The new arrivals, cards of C3 | list | The four newest products. Each card's parts are C3's. |  | The new arrivals | C3 | R1 | E7 |  |  |
| 15 | Popular searches | heading | The heading over four words to search for. |  | Popular searches |  |  | E53 |  |  |
| 16 | A popular search | link | One of four words; opens the search's results for it. Leads to SC4. |  | the word |  | R3 | E53 |  | SC4 |
| 17 | The footer, C13 | region | The row every screen ends with: the shop's line, its four pages and the fine print; each thing in it is a part of C13. |  | the footer | C13 |  | E8 |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Empty | n/a | The catalogue always has products to show: six categories of six. |  |  |
| Loading | n/a | The page arrives whole from the server; nothing on it waits for a call. |  |  |
| Error | likely |  |  | Open / on a copy of the shop with the catalogue's server stopped. |
| Hover | observed | A primary button darkens under the pointer, C1; a product's name turns blue, C3; a link of the header turns blue. | E45 |  |
| Keyboard | observed | Tab reaches the header's controls first, then each tile, card and search, then the footer, in reading order; the focus shows as a blue ring on each. | E46 |  |
| Mobile | observed | At 375 pixels the deal's picture goes under its words, the tiles are two to a row and the cards one; the search moves under the mark. Seen in evidence/captures/site/shots/V1-375.jpg. |  |  |
| Navigation | likely |  |  | Open /, scroll to New arrivals, open a product, and go back. |
| Permissions | observed | Everyone sees the same page; signed in, only the header changes (E24). | E8 |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | A category's tile is selected | SC2 | SC2 | R1 | E7 |
| normal | A product's name or picture is selected | SC3 | SC3 | R2 | E7 |
| normal | A popular search is selected | SC4 | SC4 | R3 | E53 |

## Variants

| What differs, and for whom | About |
|---|---|
| Signed in, the header greets the customer by name and offers their menu, the site header's greeting. | E24 |
