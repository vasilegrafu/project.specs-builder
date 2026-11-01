---
id: SC4
name: Search results
kind: list
address: /search?q={words}
who: anyone, signed in or not
reached by: the search in the header, on every screen; a popular search on SC1
---

Anyone who searched finds the products that hold their words, or learns that none does.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The products whose name or description holds the words, and how many they are. | R3 | N1 |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C9 | region | The row every screen starts with: the mark, the search, the account and the cart, then the six categories; each thing in it is a part of C9. | signed in: the greeting and its menu in place of Sign in and Sign up | the banner | C9 |  | E8, E24 |  |  |
| 2 | The title | heading | Results for “headphones”: the words in quotes. |  | Results for headphones |  | R3 | E18 |  |  |
| 3 | How many match | text | 5 products match. | not shown when nothing matches | the line |  | R3 | E18 |  |  |
| 4 | The results, cards of C3 | list | Each product that matches; one out of stock has Add to cart disabled. Each card's parts are C3's. |  | The results | C3 | R3 | E18, E56 |  |  |
| 5 | Nothing matches | message | Nothing matches. | when nothing matches | the message |  | R3 | E19 |  |  |
| 6 | What to try | text | Check the spelling, try fewer words, or browse a category. | when nothing matches | the line |  | R3 | E19 |  |  |
| 7 | The footer, C13 | region | The row every screen ends with: the shop's line, its four pages and the fine print; each thing in it is a part of C13. |  | the footer | C13 |  | E8 |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Empty | n/a | The page opens only for words searched; words that match nothing are No-results. |  |  |
| Loading | n/a | The page arrives whole from the server; nothing on it waits for a call. |  |  |
| Error | likely |  |  | Search on a copy of the shop with the catalogue's server stopped. |
| No-results | observed | Nothing matches, and what to try, in place of the count and the results. | E19 |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | A product's name or picture is selected | SC3 | SC3 | R2 | E18 |
| normal | Search, with words no product holds | no-results |  | R3 | E19 |
| no-results | Search, with words a product holds | normal |  | R3 | E18 |

## Variants

| What differs, and for whom | About |
|---|---|
| Signed in, the header greets the customer by name and offers their menu, the site header's greeting. | E24 |
