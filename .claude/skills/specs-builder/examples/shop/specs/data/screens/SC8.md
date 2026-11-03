---
id: SC8
name: Create an account
kind: form
address: /sign-up
who: anyone
reached by: Sign up in the header; Create an account on SC7
follows: FD1, FD2, FD3, FD4, FD5, FD7, FD8, FD9, FD10
---

A visitor makes an account, and is signed in.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The name, the email, the password twice and the terms accepted, sent to make the account. | R8 | N4, B6 |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C9 | region | The row every screen starts with: the mark, the search, the account and the cart, then the six categories; each thing in it is a part of C9. |  | the banner | C9 |  | E8 |  |  |
| 2 | The title | heading | Create an account. |  | Create an account |  |  | E28 |  |  |
| 3 | The refusal, C8 | message | Three things need a look.: how many fields are refused, above the form. | after a refused form | the message, announced when it appears | C8 | R8 | E29 |  |  |
| 4 | Full name, C7 | field | The customer's name. |  | Full name | C7 |  | E28, N4 |  |  |
| 5 | Email, C7 | field | The email the account is signed in with. | marked when refused | Email | C7 | R8 | E29, N4 |  |  |
| 6 | Why email is refused | message | "That is not an email address.", under the field, when the form is refused. | when refused | the reason, read with the field |  | R8 | E29, N4 |  |  |
| 7 | Password, C7 | field | The password: eight characters at least, with a number. | marked when refused | Password | C7 | R8 | B6, E30 |  |  |
| 8 | Why password is refused | message | "At least 8 characters, with a number.", under the field, when the form is refused. | when refused | the reason, read with the field |  | R8 | B6, E30 |  |  |
| 9 | Repeat the password, C7 | field | The password again. | marked when refused | Repeat the password | C7 | R8 | B6, E30 |  |  |
| 10 | Why repeat the password is refused | message | "The two passwords differ.", under the field, when the form is refused. | when refused | the reason, read with the field |  | R8 | B6, E30 |  |  |
| 11 | I accept the terms | field | A tick, required. |  | I accept the terms, a tick box |  | R8 | E28 |  |  |
| 12 | The terms | link | Opens the terms of sale. Leads to SC17. |  | terms |  |  | E28 |  | SC17 |
| 13 | Create account, C1 | button | Makes the account, or refuses the form. |  | Create account | C1 | R8 | E28 |  |  |
| 14 | Sign in | link | Already have one? and the link. Leads to SC7. |  | Sign in |  |  | E28 |  | SC7 |
| 15 | The footer, C13 | region | The row every screen ends with: the shop's line, its four pages and the fine print; each thing in it is a part of C13. |  | the footer | C13 |  | E8 |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Empty | observed | The fields blank, the terms not ticked. | E28 |  |
| Validation | observed | The refusal above the form; each refused field marked, its reason under it, what was typed kept. | E29 |  |
| Error | likely |  |  | Create an account with the network cut, on a copy of the shop. |
| Loading | likely |  |  | Create an account with the network slowed, on a copy of the shop. |
| Success | likely |  |  | Create an account on a copy of the shop: Create account was a stop point of the walk. |
| Disabled | n/a | Create account is always enabled; what is wrong is said when it is selected (R8). |  |  |
| Unauthorized | n/a | Anyone may make an account. |  |  |
| Hover | observed | A primary button darkens under the pointer, C1; a link of the header turns blue. | E45 |  |
| Keyboard | observed | Tab reaches each field in order, the terms, Create account and Sign in; the focus shows on each. | E46 |  |
| Mobile | observed | At 375 pixels the form takes the full width. Seen in evidence/captures/site/shots/V13-375.jpg. |  |  |
| Navigation | likely |  |  | Fill the form half, open the terms, and come back. |
| Permissions | observed | Anyone reaches it. | E28 |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Create account, with a field wrong | validation |  | R8 | E29 |
| validation | Create account, every field right | success |  | R8 | E28 |
| normal | Sign in is selected | SC7 | SC7 | R7 | E28 |
