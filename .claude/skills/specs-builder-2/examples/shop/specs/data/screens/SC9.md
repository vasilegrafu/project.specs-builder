---
id: SC9
name: Forgot your password
kind: form
address: /forgot-password, and /forgot-password-sent after
who: anyone
reached by: Forgot your password? on SC7
---

A customer who has forgotten their password asks for a link to choose a new one.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The email, sent to ask for a link; the link is sent only where an account has it, and the page says the same either way. | R9 | N4, B7 |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C9 | region | The row every screen starts with: the mark, the search, the account and the cart, then the six categories; each thing in it is a part of C9. |  | the banner | C9 |  | E8 |  |  |
| 2 | The title | heading | Forgot your password? | not shown once sent | Forgot your password? |  | R9 | E31 |  |  |
| 3 | What it does | text | Tell us your email and we send a link to choose a new one. | not shown once sent | the line |  | R9 | E31 |  |  |
| 4 | Email, C7 | field | The account's email. |  | Email | C7 | R9 | E31, N4 |  |  |
| 5 | Send the link, C1 | button | Asks for the link. | not shown once sent | Send the link | C1 | R9 | E31 |  |  |
| 6 | Check your email | heading | Check your email. | once sent | Check your email |  | R9 | E32 |  |  |
| 7 | The words after | text | If an account has that address, a link is on its way. It works for one hour. | once sent | the line |  | R9 | B7, E32 |  |  |
| 8 | Back to sign in | link | Back to sign in. Leads to SC7. | once sent | Back to sign in |  |  | E32 |  | SC7 |
| 9 | The footer, C13 | region | The row every screen ends with: the shop's line, its four pages and the fine print; each thing in it is a part of C13. |  | the footer | C13 |  | E8 |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Empty | observed | The email blank: the page as it opens. | E31 |  |
| Validation | likely |  |  | Send the link with "ana@" as the email, on a copy of the shop. |
| Error | likely |  |  | Send the link with the network cut, on a copy of the shop. |
| Loading | likely |  |  | Send the link with the network slowed, on a copy of the shop. |
| Success | observed | Check your email and the words after, in place of the form, whether or not an account has the email. | E32 |  |
| Disabled | n/a | Send the link is always enabled. |  |  |
| Unauthorized | n/a | Anyone may ask for a link. |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Send the link, with an email | success |  | R9 | E32 |
| success | Back to sign in is selected | SC7 | SC7 | R7 | E32 |
