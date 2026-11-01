---
id: SC8
name: Monthly figures
kind: page
address: /staff/figures
who: signed-in staff
reached by: Monthly figures on C2
shows: R7, R8, R20, R22
---

Staff read the numbers behind the goals, month by month.

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The staff header, C2 | region | The row every staff screen starts with; each thing in it is a part of C2. |  | the header | C2 |  |  |  |  |
| 2 | The heading | heading | Monthly figures |  | Monthly figures |  |  |  |  |  |
| 3 | Nothing yet | text | No figures yet. | shown on empty | No figures yet |  | R8 |  |  |  |
| 4 | Could not load | message | The figures could not be shown, with a way to try again. | shown on error | Could not load | C6 | R8 |  |  |  |
| 5 | The table | table | One row a calendar month, the latest first, for as long as the 12 months keep its feedback. |  | Monthly figures, a table |  | R8 |  |  |  |
| 6 | The columns' names | text | Month, Feedback, Average rating, Requests sent, Opt-outs. |  | the columns |  | R8 |  |  |  |
| 7 | The month | text | The calendar month. |  | the month |  | R8 |  |  |  |
| 8 | Feedback | text | How many pieces arrived, leaving out those removed; 0 where there were none. |  | feedback |  | R8 |  |  |  |
| 9 | Average rating | text | The month's average; none, rather than zero, where it had no ratings. |  | average rating |  | R7 |  |  |  |
| 10 | Requests sent | text | How many requests went out. |  | requests sent |  | R20 |  |  |  |
| 11 | Opt-outs | text | How many customers opted out. |  | opt-outs |  | R20 |  |  |  |
| 12 | Opt-outs' heading | heading | Who opted out |  | Who opted out |  | R22 |  |  |  |
| 13 | An opt-out | text | The customer's address and the date; repeated for each, the latest first. |  | an opt-out |  | R22 |  |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| empty | added | No figures yet. |  |  |
| loading | added | The heading, while the figures arrive. |  |  |
| error | added | Could not load, with a way to try again. |  |  |
| unauthorized | added | Signed out, the address leads to SC5, and no figures show. |  |  |
| hover | added | A link or button marks itself under the pointer; a touch screen has nothing in its place. |  |  |
| keyboard | added | Tab reaches the header, then each button in order; the focus always shows. |  |  |
| mobile | added | At 375 pixels everything stands in one column at full width; a table scrolls on its own. |  |  |
| navigation | added | Back leaves the page; the address opens it as it stands now. |  |  |
| permissions | added | Only signed-in staff. |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Feedback is selected | SC6 | SC6 | R3 |  |
| normal | Sign out is pressed | SC5 | SC5 | R23 |  |
