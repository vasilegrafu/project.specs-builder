---
id: SC5
name: My visits
kind: list
address: /visits
who: the patient, signed in; their own visits alone
reached by: My visits in the header, signed in; My visits on SC4 and SC7; signing in on SC8
follows: FD1, FD2, FD3, FD4, FD5, FD7, FD8, FD9, FD10
---

A patient sees the visits they have coming up and the past ones, and opens one.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The patient's visits: number, when, with whom, what about and status, those coming up apart from the past ones. | R5 | N1 |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C4 | region | The row every screen starts with: the mark, the clinic's four links, then the patient's own; each thing in it is a part of C4. | always signed in | the banner | C4 |  | E10, E11 |  |  |
| 2 | A column's name | text | Visit, When, With, About, Status: what the cells under it say. |  | the column's name |  |  | E26, N1 |  |  |
| 3 | A visit's number | link | In each row of both tables: the visit's number, which leads to SC6, the visit. |  | the number |  | R5 | E26, N1 |  | SC6 |
| 4 | Its time | text | The day and the time of the visit. |  | the time |  | R5 | E26, N1 |  |  |
| 5 | With whom | text | The one the visit is with. |  | the name |  |  | N1, N2 |  |  |
| 6 | About what | text | What the visit is about, as written when booked. |  | the reason |  |  | E26, N1 |  |  |
| 7 | Its status, C7 | text | Booked, Attended or Cancelled. |  | the status | C7 |  | E28, N1 |  |  |
| 8 | The title | heading | My visits. |  | My visits |  |  | E26 |  |  |
| 9 | Coming up | heading | The heading over the visits booked. |  | Coming up |  |  | E26 |  |  |
| 10 | The visits coming up | table | Visit, When, With, About and Status, one row a visit booked, each status a C7. | not when empty | a table of five columns | C7 | R5 | E26, N1 |  |  |
| 11 | None booked | text | No visits booked. Your next one shows here once it is booked. | empty | the line |  | R5 | E27 |  |  |
| 12 | Book another visit, C1 | link | To book one more. Leads to SC4. | not when empty | Book another visit | C1 | R2 |  |  | SC4 |
| 13 | Book a visit, C1 | link | To book one. Leads to SC4. | empty | Book a visit | C1 | R2 |  |  | SC4 |
| 14 | Past visits | heading | The heading over the visits past. | not when empty | Past visits |  |  | E26 |  |  |
| 15 | The past visits | table | The same columns, one row a visit attended or cancelled, each status a C7. | not when empty | a table of five columns | C7 | R5 | E26, E28, N1 |  |  |
| 16 | The footer, C5 | region | The row every screen ends with: the clinic's line, three pages about the clinic and the line on emergencies; each thing in it is a part of C5. |  | the footer | C5 |  | E10 |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Empty | observed | "Coming up", None booked and Book a visit; no table and no past visits. | E27 |  |
| Loading | n/a | It arrives whole, with nothing to wait for. |  |  |
| Error | likely |  |  | Open My visits on a copy of the site with the appointments system stopped. |
| No-results | n/a | The list is neither searched nor filtered. |  |  |
| Hover | observed | A primary button darkens under the pointer, C1; a link of the header turns green and is underlined. | E51, E61 |  |
| Keyboard | observed | Tab reaches the header's links, each visit's number in order, and Book another visit; the focus shows on each. | E55 |  |
| Mobile | observed | At 375 pixels each visit is a block of lines, its number first and its status last, with no heads. Seen in evidence/captures/site/shots/V10-375.jpg. |  |  |
| Navigation | likely |  |  | Open a visit, go back, and reload My visits. |
| Permissions | likely |  |  | Open /visits.html signed out on a copy of the site, and see what shows. |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | A visit's number is selected | SC6 | SC6 | R5 | E26 |
| normal | Book another visit is selected | SC4 | SC4 | R2 | E26 |
| empty | Book a visit is selected | SC4 | SC4 | R2 | E27 |
