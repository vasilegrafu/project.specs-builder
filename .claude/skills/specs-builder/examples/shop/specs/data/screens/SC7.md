---
id: SC7
name: Sign in
kind: form
address: /sign-in
who: anyone; a customer signed in already is greeted in the header
reached by: Sign in in the header; a page that needs an account; Sign in again on SC10
follows: FD1, FD2, FD3, FD4, FD5, FD7, FD8, FD9, FD10
---

A visitor with an account signs in, and comes back to what they were doing.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The email and the password, and whether to keep the session, sent to sign in. | R7 | N4 |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C9 | region | The row every screen starts with: the mark, the search, the account and the cart, then the six categories; each thing in it is a part of C9. |  | the banner | C9 |  | E8 |  |  |
| 2 | The title | heading | Sign in. |  | Sign in |  |  | E26 |  |  |
| 3 | The refusal, C8 | message | The email or the password is wrong., above the form, after a refused sign-in. | after a refused sign-in | the message, announced when it appears | C8 | R7 | E27 |  |  |
| 4 | Email, C7 | field | The account's email. |  | Email | C7 | R7 | E26, N4 |  |  |
| 5 | Password, C7 | field | The password, as dots. |  | Password | C7 | R7 | E26, N4 |  |  |
| 6 | Keep me signed in | field | A tick: the session outlives the browser. |  | Keep me signed in, a tick box |  | R7 | E26 |  |  |
| 7 | Sign in, C1 | button | Signs in; a wrong pair is refused above the form. |  | Sign in | C1 | R7 | E26 |  |  |
| 8 | Forgot your password? | link | Opens the password page. Leads to SC9. |  | Forgot your password? |  |  | E26 |  | SC9 |
| 9 | Create an account | link | New here? and the link. Leads to SC8. |  | Create an account |  |  | E26 |  | SC8 |
| 10 | The footer, C13 | region | The row every screen ends with: the shop's line, its four pages and the fine print; each thing in it is a part of C13. |  | the footer | C13 |  | E8 |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Empty | observed | The two fields blank: the page as it opens. | E26 |  |
| Validation | observed | The refusal above the form; Email and Password marked, keeping what was typed. | E27 |  |
| Error | likely |  |  | Sign in with the network cut, on a copy of the shop. |
| Loading | likely |  |  | Sign in with the network slowed, on a copy of the shop. |
| Success | likely |  |  | Sign in as the test customer on a copy of the shop, and see which page opens. |
| Disabled | n/a | Sign in is always enabled; a blank field is refused as a wrong one is (R7). |  |  |
| Unauthorized | n/a | Anyone may sign in. |  |  |
| Hover | observed | A primary button darkens under the pointer, C1; a link of the header turns blue. | E45 |  |
| Keyboard | observed | Tab reaches Email, Password, Keep me signed in, Sign in, Forgot your password? and Create an account; the focus shows on each. | E46 |  |
| Mobile | observed | At 375 pixels the form takes the full width. Seen in evidence/captures/site/shots/V11-375.jpg. |  |  |
| Navigation | likely |  |  | Open /checkout signed out, sign in, and see which page opens. |
| Permissions | observed | Anyone reaches it, signed in or not. | E26 |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Sign in, with an email or a password that is wrong | validation |  | R7 | E27 |
| validation | Sign in, with the account's email and password | success |  | R7 | E26 |
| normal | Forgot your password? is selected | SC9 | SC9 | R9 | E26 |
| normal | Create an account is selected | SC8 | SC8 | R8 | E26 |

## Layout

| What | Must be | From |
|---|---|---|
| The form | 520 pixels wide at most, in the middle of the page | foundations |
| The refusal | the full width of the form, above the fields | E27 |
