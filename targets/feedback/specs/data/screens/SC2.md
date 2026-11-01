---
id: SC2
name: Stop feedback requests
kind: form
address: /stop/<the customer's own link>
who: the customer the link belongs to
reached by: the Stop link in a request, SC3 or SC4
shows: R17, R22
---

A customer stops being asked for feedback.

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The business's name | text | [Business name], at the top of the page. |  | the business's name | C9 |  |  | Q17 |  |
| 2 | The heading | heading | Stop feedback requests? |  | Stop feedback requests? |  |  |  |  |  |
| 3 | The line | text | Says what stopping does, and that feedback can still be sent. |  | the line |  | R17 |  |  |  |
| 4 | Stop asking me | button | Opts the customer out, and keeps the date. | sending | Stop asking me | C3 | R17 |  |  |  |
| 5 | Could not be done | message | Above the button, when the opt-out could not be kept. | shown on error | Could not be done | C6 | R17 |  |  |  |
| 6 | Link not valid | message | When the link is not one the website gave. | shown on not-found | Link not valid | C6 | R17 |  |  |  |
| 7 | You are opted out | heading | You won't be asked again. | shown on success | You won't be asked again |  | R17 |  |  |  |
| 8 | Still welcome | text | Says feedback can still be sent, with a link to the feedback page. | shown on success | the line |  | R17 |  |  | SC1 |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| empty | n/a | n/a: there is nothing to fill in. |  |  |
| validation | n/a | n/a: there is nothing to check. |  |  |
| error | added | Could not be done, above the button, which can be pressed again. |  |  |
| loading | added | Stop asking me cannot be pressed again. |  |  |
| success | added | You won't be asked again. |  |  |
| not-found | added | Link not valid. |  |  |
| disabled | n/a | n/a: the page is always open to its link. |  |  |
| unauthorized | n/a | n/a: the link stands for the customer. |  |  |
| hover | added | The fields and buttons mark themselves under the pointer; a touch screen has nothing in its place. |  |  |
| keyboard | added | Tab reaches the fields in order, then the button; the focus always shows; Enter sends. |  |  |
| mobile | added | At 375 pixels everything stands in one column at full width. |  |  |
| navigation | added | Back leaves the page; a reload keeps nothing that was typed. |  |  |
| permissions | added | Only the link's own customer reaches it. |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Stop asking me is pressed | loading |  | R17 |  |
| loading | The opt-out is kept | success |  | R17 |  |
| loading | The opt-out cannot be kept | error |  | R17 |  |
| success | The link to the feedback page is selected | SC1 | SC1 | R17 |  |
