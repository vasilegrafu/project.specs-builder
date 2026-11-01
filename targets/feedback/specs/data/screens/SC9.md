---
id: SC9
name: Link and QR code
kind: page
address: /staff/print
who: signed-in staff
reached by: Link and QR code on C2
shows: R16
---

Staff save the link and QR code to print on receipts and in parcels.

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The staff header, C2 | region | The row every staff screen starts with; each thing in it is a part of C2. |  | the header | C2 |  |  |  |  |
| 2 | The heading | heading | Link and QR code |  | Link and QR code |  | R16 |  |  |  |
| 3 | The line | text | Says what they are for. |  | the line |  | R16 |  |  |  |
| 4 | The link | text | The feedback page's address. |  | the link |  | R16 |  | Q17 |  |
| 5 | Copy the link | button | Copies the address. |  | Copy the link | C3 | R16 |  |  |  |
| 6 | The QR code | image | The QR code of that address. |  | QR code to the feedback page |  | R16 |  |  |  |
| 7 | Save the QR code | button | Saves it as a picture, to print. |  | Save the QR code | C3 | R16 |  |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| empty | n/a | n/a: the link and QR code are always there. |  |  |
| loading | n/a | n/a: it arrives whole. |  |  |
| error | n/a | n/a: it asks nothing further of the server. |  |  |
| unauthorized | added | Signed out, the address leads to SC5. |  |  |
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
