---
id: SC6
name: The feedback list
kind: list
address: /staff
who: signed-in staff
reached by: signing in, SC5; Feedback on C2; the link in SC10
shows: R3, R5, R6, R9, R10, R12, R22
---

Staff read every piece of feedback, the newest first, and see what needs attention.

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The staff header, C2 | region | The row every staff screen starts with; each thing in it is a part of C2. |  | the header | C2 |  |  |  |  |
| 2 | The heading | heading | Feedback |  | Feedback |  | R3 |  |  |  |
| 3 | Nothing yet | text | No feedback yet. | shown on empty | No feedback yet |  | R3 |  |  |  |
| 4 | Could not load | message | The feedback could not be shown, with a way to try again. | shown on error | Could not load | C6 | R3 |  |  |  |
| 5 | The list | list | Every piece of feedback not removed, the newest first; each item holds the elements below. |  | a list of feedback | C8 | R3 |  |  |  |
| 6 | When it arrived | text | The date and time. |  | the date and time |  | R2 |  |  |  |
| 7 | The rating, C1 | group | The stars and the number; left out where the customer gave none. | read only | Rating, out of 5 stars | C1 | R6 |  |  |  |
| 8 | Unhappy | mark | The word Unhappy, on feedback rated 1 or 2 stars. | hidden on 3 stars or more, or no rating | Unhappy | C7 | R10 |  |  |  |
| 9 | What they wrote | text | The customer's words; left out where they wrote none. |  | the feedback |  | R3 |  |  |  |
| 10 | Reply by email | link | The customer's address, opening the member of staff's own email program; left out where they gave none. |  | Reply by email |  | R5 |  |  |  |
| 11 | May be published | mark | May be published, with the date; or Not for publishing. | may be published; not for publishing | May be published | C7 | R22 |  |  |  |
| 12 | Remove | button | Asks to confirm. Leads to SC7. |  | Remove | C3 | R12 |  |  | SC7 |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| empty | added | No feedback yet. |  |  |
| loading | added | The heading, while the list arrives. |  |  |
| error | added | Could not load, with a way to try again. |  |  |
| no-results | n/a | n/a: the list has no search or filter. |  |  |
| unauthorized | added | Signed out, the address leads to SC5, and no feedback shows. |  |  |
| hover | added | A link or button marks itself under the pointer; a touch screen has nothing in its place. |  |  |
| keyboard | added | Tab reaches the header, then each item's links and buttons in order; the focus always shows. |  |  |
| mobile | added | At 375 pixels each item stands at full width, its parts one above the other. |  |  |
| navigation | added | Back leaves the page; the address opens the list as it stands now. |  |  |
| permissions | added | Only signed-in staff. |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Remove is pressed | SC7 | SC7 | R12 |  |
| normal | Monthly figures is selected | SC8 | SC8 |  |  |
| normal | Link and QR code is selected | SC9 | SC9 | R16 |  |
| normal | Sign out is pressed | SC5 | SC5 | R23 |  |
