---
id: SC3
name: A product
kind: detail
address: /p/{slug}
who: anyone, signed in or not
reached by: a product's card on SC1, SC2 and SC4, and under You may also like here
displays: N1.in, N1.low, N1.out
follows: FD1, FD2, FD3, FD4, FD5, FD6, FD7, FD8, FD9, FD10
---

A visitor reads one product -- its price, its stock, what it is -- and puts it in the cart.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The product: its name, picture, stars and count of reviews, SKU, price and old price, stock, line, specifications and reviews. | R2 | N1 |
| Three more products of its category. | R2 |  |
| Add to cart sends the product and the quantity to the cart. | R4 |  |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C9 | region | The row every screen starts with: the mark, the search, the account and the cart, then the six categories; each thing in it is a part of C9. | signed in: the greeting and its menu in place of Sign in and Sign up | the banner | C9 |  | E8, E24 |  |  |
| 2 | Home, in the crumbs | link | The first of the crumbs. Leads to SC1. |  | Home |  |  | E13 |  | SC1 |
| 3 | The category, in the crumbs | link | The product's category. Leads to SC2. |  | Laptops |  |  | E13 |  | SC2 |
| 4 | The product, in the crumbs | text | Where the visitor stands. |  | Aero 14 |  |  | E13 |  |  |
| 5 | The picture | picture | The product, as the catalogue has it. |  | the product's name |  |  | E13, N1 |  |  |
| 6 | The name | heading | Aero 14. |  | Aero 14 |  |  | E13, N1 |  |  |
| 7 | The count of reviews | link | 212 reviews, under the stars; leads down to the reviews. |  | 212 reviews |  |  | E13 |  |  |
| 8 | The SKU | text | SKU LT-AER-14: the warehouse's code. |  | SKU LT-AER-14 |  |  | E13, N1 |  |  |
| 9 | The price, C4 | text | €1,099.00, the old price struck out and Deal. |  | the price | C4 | R2 | B8, E13 |  |  |
| 10 | The stock, C5 | text | In stock; Only a few left with three or fewer; Out of stock with none. | few left; out of stock | the stock, as it reads | C5 | R2 | E15, E16 |  |  |
| 11 | The line about it | text | What the product is, in one line. |  | the line |  |  | E13 |  |  |
| 12 | Quantity | field | A number from 1 to 5, 1 to start. |  | Quantity |  | R4 | B1, E14 |  |  |
| 13 | Add to cart, C1 | button | Adds the product in that quantity to the cart and opens SC5. | disabled when out of stock (E15) | Add to cart | C1 | R4 | B5 | Q1 |  |
| 14 | Tell me when it is back | link | Out of stock only: offers to tell the customer when it is back. | out of stock only | Tell me when it is back |  |  | E15 |  |  |
| 15 | A promise | text | One of three: Free delivery over €50, 30-day returns, 2-year warranty. |  | the promise |  |  | B2, E17 |  |  |
| 16 | Specifications | heading | The heading over the table of specifications. |  | Specifications |  |  | E13 |  |  |
| 17 | A specification's name | text | Screen, Processor, Memory and the rest, one to a row. |  | the name |  |  | E13, N1 |  |  |
| 18 | A specification's value | text | The value beside its name. |  | the value |  |  | E13, N1 |  |  |
| 19 | Reviews | heading | The heading over the reviews. |  | Reviews |  |  | E13 |  |  |
| 20 | The rating | text | The stars and 4.6 out of 5, from 212 reviews. |  | 4.6 out of 5, from 212 reviews |  |  | E13 |  |  |
| 21 | Who reviewed | text | The reviewer's initials, and verified purchase. |  | M. K., verified purchase |  |  | E13 |  |  |
| 22 | A review | text | What the reviewer said. |  | the review |  |  | E13 |  |  |
| 23 | You may also like | heading | The heading over three more products. |  | You may also like |  |  | E13 |  |  |
| 24 | More products, cards of C3 | list | Three products of the category. Each card's parts are C3's. |  | More products | C3 | R2 | E13 |  |  |
| 25 | The footer, C13 | region | The row every screen ends with: the shop's line, its four pages and the fine print; each thing in it is a part of C13. |  | the footer | C13 |  | E8 |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Loading | n/a | The page arrives whole from the server; nothing on it waits for a call. |  |  |
| Error | likely |  |  | Open /p/aero-14.html on a copy of the shop with the catalogue's server stopped. |
| Not-found | observed | An address of a product that does not exist gets the server's bare error page today; the rebuilt shop shows SC18 (R16). | E43 |  |
| Unauthorized | n/a | Anyone may see a product. |  |  |
| Few-left | observed | The stock says "Only a few left", in amber. | E16 |  |
| Out-of-stock | observed | The stock says "Out of stock", Add to cart is disabled, and Tell me when it is back is offered. | E15 |  |
| Hover | observed | A primary button darkens under the pointer, C1; a product's name turns blue, C3; a link of the header turns blue. | E45 |  |
| Keyboard | observed | Tab reaches the header, the crumbs, 212 reviews, Quantity, Add to cart, then each card below; the focus shows on each. | E46 |  |
| Mobile | observed | At 375 pixels the picture stands above the facts, and You may also like is one card to a row. Seen in evidence/captures/site/shots/V5-375.jpg. |  |  |
| Navigation | likely |  |  | Open /p/aero-14.html, add it, then go back from the cart. |
| Permissions | likely |  |  | Open a product signed in and signed out, and compare. |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Add to cart is selected | SC5 | SC5 | R4 | E14 |
| normal | The stock falls to three or fewer | few-left |  | R2 | E16 |
| few-left | The stock runs out | out-of-stock |  | R2 | E15 |
| normal | Another product, under You may also like | SC3 | SC3 | R2 | E13 |
| any | the address names no product | SC18 | SC18 | R16 | E43 |

## Variants

| What differs, and for whom | About |
|---|---|
| Signed in, the header greets the customer by name and offers their menu, the site header's greeting. | E24 |

## Layout

| What | Must be | From |
|---|---|---|
| The picture and the facts | two columns of equal width, the picture at the left; one column under 800 pixels | foundations |
| Quantity and Add to cart | on one line, Quantity first | E13 |
