---
id: SC6
name: A visit
kind: detail
address: /visits/{number}
who: the patient whose visit it is, signed in
reached by: a visit's number on SC5; See this visit on SC4; Keep it on SC7
displays: N1.attended, N1.booked, N1.cancelled
---

A patient sees one of their visits, and cancels it while it is more than 24 hours away.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The visit: number, status, with whom, when, what about and where. | R5 | N1 |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C4 | region | The row every screen starts with: the mark, the clinic's four links, then the patient's own; each thing in it is a part of C4. | always signed in | the banner | C4 |  | E10, E11 |  |  |
| 2 | The way back | link | My visits › LC-2041: My visits leads to SC5. |  | My visits |  |  | E29 |  | SC5 |
| 3 | The title | heading | Visit LC-2041. |  | Visit LC-2041 |  |  | E59, N1 |  |  |
| 4 | The status, C7 | text | Booked; Attended; Cancelled. | by the state | the status | C7 |  | E28, N1 |  |  |
| 5 | The facts | region | With, When, About and Where, each with its value. |  | the visit's facts |  |  | E29, N1 |  |  |
| 6 | A fact's name | text | With, When, About or Where: what the value beside it is. |  | the name |  |  | N1 |  |  |
| 7 | The name | link | The one the visit is with. Leads to SC3. |  | Dr Amara Okafor |  | R1 | N2 |  | SC3 |
| 8 | When | text | The day and the time of the visit. |  | the day and time |  |  | E29, N1 |  |  |
| 9 | About what | text | What the visit is about, as written when booked. |  | the reason |  |  | E29, N1 |  |  |
| 10 | Where | text | The clinic's address. |  | the address |  |  | E29, E46 |  |  |
| 11 | Cancel this visit, C3 | link | Opens the question whether to cancel it. Leads to SC7. | booked only | Cancel this visit | C3 | R6 | B3, E29 |  | SC7 |
| 12 | Book another with, C2 | link | Book another with Dr Amara Okafor: the form with that one chosen. Leads to SC4. | booked only | Book another with Dr Amara Okafor | C2 | R4 | E29 |  | SC4 |
| 13 | The rule | text | A visit can be cancelled up to 24 hours before it starts; later, call the clinic. | booked only | the line |  |  | B3, E30 |  |  |
| 14 | Attended | text | This visit has taken place. Nothing more to do with it. | attended | the line |  | R5 | E31 |  |  |
| 15 | Cancelled | text | This visit was cancelled on 12 August 2026: the day it was cancelled. | cancelled | the line |  | R5 | E32 |  |  |
| 16 | The footer, C5 | region | The row every screen ends with: the clinic's line, three pages about the clinic and the line on emergencies; each thing in it is a part of C5. |  | the footer | C5 |  | E10 |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Loading | n/a | It arrives whole, with nothing to wait for. |  |  |
| Error | likely |  |  | Open a visit on a copy of the site with the appointments system stopped. |
| Not-found | likely |  |  | Open /visits/LC-9999.html signed in as the test patient. |
| Unauthorized | likely |  |  | Open another patient's visit by its number, signed in as the test patient, on a copy of the site. |
| Attended | observed | "Attended", the line that says it has taken place, and nothing to do. | E31 |  |
| Cancelled | observed | "Cancelled", the day it was cancelled, and nothing to do. | E32 |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Cancel this visit is selected | SC7 | SC7 | R6 | E29 |
| normal | Book another with is selected | SC4 | SC4 | R4 | E29 |
| any | My visits, above the title, is selected | SC5 | SC5 | R5 | E29 |
