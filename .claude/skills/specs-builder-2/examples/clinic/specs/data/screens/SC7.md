---
id: SC7
name: Cancel a visit
kind: dialog
address: /visits/{number}-cancel; the visit cancelled, /cancelled
who: the patient whose visit it is, signed in, while the visit is more than 24 hours away (B3)
reached by: Cancel this visit on SC6
---

A patient confirms that a visit is to be cancelled, knowing it cannot be undone, and sees it cancelled.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The visit to cancel: its number, with whom, when. | R6 | N1 |
| Cancel the visit cancels it, frees its time, and sends a note to the patient's email. | R6 | B2, B6 |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C4 | region | The row every screen starts with: the mark, the clinic's four links, then the patient's own; each thing in it is a part of C4. | always signed in | the banner | C4 |  | E10, E11 |  |  |
| 2 | The way back | link | My visits › LC-2041 › Cancel: My visits leads to SC5, the number to SC6. | not in success | My visits |  |  | E33 |  | SC5 |
| 3 | The question | heading | Cancel visit LC-2041? | not in success | Cancel visit LC-2041? |  | R6 | E33 |  |  |
| 4 | What it means | text | Your visit with Dr Amara Okafor on 16 October 2026 at 09:30 will be cancelled and the time given to someone else. This cannot be undone. | not in success | the line |  | R6 | B2, E33 |  |  |
| 5 | Cancel the visit, C3 | button | Cancels the visit. | not in success | Cancel the visit | C3 | R6 | B3, E33 |  |  |
| 6 | Keep it, C2 | link | The visit kept. Leads to SC6. | not in success | Keep it | C2 | R6 | E33 |  | SC6 |
| 7 | Cancelled | heading | Visit cancelled. | success | Visit cancelled |  | R6 | E34 |  |  |
| 8 | The note sent | text | Visit LC-2041 with Dr Amara Okafor on 16 October 2026 is cancelled. We have sent a note to the email. | success | the line |  |  | B6, E34 |  |  |
| 9 | Book another visit, C1 | link | To book one more. Leads to SC4. | success | Book another visit | C1 | R2 | E34 |  | SC4 |
| 10 | My visits, C2 | link | To the patient's visits. Leads to SC5. | success | My visits | C2 | R5 | E34 |  | SC5 |
| 11 | The footer, C5 | region | The row every screen ends with: the clinic's line, three pages about the clinic and the line on emergencies; each thing in it is a part of C5. |  | the footer | C5 |  | E10 |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Loading | likely |  |  | Cancel a visit with the network slowed, on a copy of the site. |
| Error | likely |  |  | Cancel a visit on a copy of the site with the appointments system stopped. |
| Success | observed | The visit cancelled in place of the question, with the note sent and the two ways on. | E34 |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Cancel the visit is selected | success |  | R6 | E34 |
| normal | Keep it is selected | SC6 | SC6 | R6 | E33 |
| success | Book another visit is selected | SC4 | SC4 | R2 | E34 |
| success | My visits is selected | SC5 | SC5 | R5 | E34 |
