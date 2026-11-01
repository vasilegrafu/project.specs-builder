---
id: SC1
name: Give feedback
kind: form
address: /
who: anyone
reached by: the link in a request, SC3 or SC4; the printed link or QR code
shows: R1, R2, R5, R6, R9
---

A customer gives a rating, a message, or both, with no account.

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The business's name | text | [Business name], at the top of the page. |  | the business's name | C9 |  |  | Q17 |  |
| 2 | The heading | heading | How did we do? |  | How did we do? |  |  |  |  |  |
| 3 | The line | text | Says what the page is for, and that no account is needed. |  | the line |  | R1 |  |  |  |
| 4 | Nothing to send | message | Above the form, when Send is pressed with everything empty. | shown on validation | Nothing to send | C6 | R1 |  |  |  |
| 5 | Not received | message | Above the form, when the feedback could not be kept; what was written stays. | shown on error | Not received | C6 | R1 |  |  |  |
| 6 | The rating's label | text | Your rating |  | Your rating |  | R6 |  |  |  |
| 7 | The rating, C1 | group | Five stars to pick from, or none. | none picked; picked | Rating, out of 5 stars | C1 | R6 |  |  |  |
| 8 | Your feedback | field | What the customer wants to say, in their own words. |  | Your feedback | C4 | R1 |  |  |  |
| 9 | Your email address | field | Optional, for a reply. |  | Your email address, optional | C4 | R5 |  |  |  |
| 10 | The address's message | message | Under the field, when the address does not look right; what was written stays. | shown on bad-address | That email address does not look right | C6 | R5 |  |  |  |
| 11 | Permission to publish | checkbox | Unticked until the customer ticks it. | unticked; ticked | You may publish what I wrote | C5 | R9 |  |  |  |
| 12 | Send | button | Sends the feedback. While sending it says Sending and cannot be pressed again. | sending | Send | C3 | R1 |  |  |  |
| 13 | Thank you | heading | Thank you, when the feedback has been kept. | shown on success | Thank you |  | R1 |  |  |  |
| 14 | Received | text | Says the feedback was received. | shown on success | the line |  | R1 |  |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| empty | added | The form with nothing filled in. |  |  |
| validation | added | Nothing to send, above the form; nothing is kept. |  |  |
| bad-address | added | Under the email field, and what was written stays. |  |  |
| error | added | Not received, above the form, and what was written stays. |  |  |
| loading | added | Send says Sending and cannot be pressed again. |  |  |
| success | added | Thank you, and the form goes. |  |  |
| disabled | n/a | n/a: the form is always open. |  |  |
| unauthorized | n/a | n/a: anyone may send feedback. |  |  |
| hover | added | The fields and buttons mark themselves under the pointer; a touch screen has nothing in its place. |  |  |
| keyboard | added | Tab reaches the fields in order, then the button; the focus always shows; Enter sends. |  |  |
| mobile | added | At 375 pixels everything stands in one column at full width. |  |  |
| navigation | added | Back leaves the page; a reload keeps nothing that was typed. |  |  |
| permissions | added | Anyone sees the same page. |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Send is pressed with everything empty | validation |  | R1 |  |
| normal | Send is pressed with an address that does not look right | bad-address |  | R5 |  |
| normal | Send is pressed with a rating, a message, or both | loading |  | R1 |  |
| loading | The feedback is kept | success |  | R2 |  |
| loading | The feedback cannot be kept | error |  | R1 |  |
