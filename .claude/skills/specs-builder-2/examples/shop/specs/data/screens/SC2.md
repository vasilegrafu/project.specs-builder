---
id: SC2
name: A category
kind: list
address: /c/{category}/index.html, and its later pages /c/{category}/page-2.html
who: anyone, signed in or not
reached by: a category in the header, on every screen; a tile on SC1
---

A visitor looks through one category's products, sorts and filters them, and opens one.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The category's name and its line, and its products four to a page, in the order chosen, from the catalogue. | R1 | N1 |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C9 | region | The row every screen starts with: the mark, the search, the account and the cart, then the six categories; each thing in it is a part of C9. | signed in: the greeting and its menu in place of Sign in and Sign up | the banner | C9 |  | E8, E24 |  |  |
| 2 | Home, in the crumbs | link | The first of the crumbs. Leads to SC1. |  | Home |  |  | E9 |  | SC1 |
| 3 | The category, in the crumbs | text | Where the visitor stands. |  | Laptops |  |  | E9 |  |  |
| 4 | The title | heading | The category's name: Laptops. |  | Laptops |  |  | E9, N1 |  |  |
| 5 | The category's line | text | What the category holds, in one line. |  | the line |  |  | E9 |  |  |
| 6 | Where the list stands | text | Showing 1–4 of 6 products. |  | the line |  | R1 | E9 |  |  |
| 7 | Sort by | field | Featured, Price: low to high, Price: high to low, Rating, Newest. |  | Sort by, a list of five |  | R1 | E10 |  |  |
| 8 | Apply, C2 | button | Sorts the list in the order chosen. |  | Apply | C2 | R1 | E10 |  |  |
| 9 | A filter | field | A price band, In stock only, or a rating from; each a tick or a choice. | hidden under 1000 pixels | the filter's words |  | R1 | E11, E49 |  |  |
| 10 | A filter's name | text | Price, Availability or Rating: what the ticks under it choose. |  | the group's name |  | R1 | E11 |  |  |
| 11 | Filters | heading | The heading of the filters. |  | Filters |  |  | E11 |  |  |
| 12 | The products, cards of C3 | list | The page's four products. Each card's parts are C3's. |  | The products | C3 | R1 | E9 |  |  |
| 13 | The pages, C12 | navigation | The pages of the list, the one open marked; each link is a part of C12. |  | Pages | C12 | R1 | E12 |  |  |
| 14 | The footer, C13 | region | The row every screen ends with: the shop's line, its four pages and the fine print; each thing in it is a part of C13. |  | the footer | C13 |  | E8 |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Empty | n/a | A category always has products: six in each (E9). |  |  |
| Loading | n/a | The page arrives whole from the server; nothing on it waits for a call. |  |  |
| Error | likely |  |  | Open /c/laptops/index.html on a copy of the shop with the catalogue's server stopped. |
| No-results | likely |  |  | Tick Over €800 and In stock only in Accessories, and apply them. |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | A product's name or picture is selected | SC3 | SC3 | R2 | E9 |
| normal | A page's number, Previous or Next is selected | normal |  | R1 | E12 |
| normal | A sort order is chosen and Apply selected | normal |  | R1 | E10 |
| normal | Home, in the crumbs | SC1 | SC1 | R1 | E9 |

## Variants

| What differs, and for whom | About |
|---|---|
| Signed in, the header greets the customer by name and offers their menu, the site header's greeting. | E24 |

## Layout

| What | Must be | From |
|---|---|---|
| The filters | 220 pixels wide, at the left of the products; hidden under 1000 pixels | E49 |
| The products | three to a row beside the filters, two under 800 pixels, one under 480 | E49 |
| The pages | under the products, centred | E12 |
