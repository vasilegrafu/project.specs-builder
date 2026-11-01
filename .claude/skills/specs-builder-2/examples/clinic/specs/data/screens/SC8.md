---
id: SC8
name: Sign in
kind: form
address: /sign-in
who: anyone with an account; a visitor without one books a first visit instead (E37)
reached by: Sign in in the header, signed out; Sign in again on SC9
---

A patient signs in to see and book their visits.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The email and the password, and whether to keep the patient signed in on the device, sent to sign in. | R8 | N3 |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C4 | region | The row every screen starts with: the mark, the clinic's four links, then the patient's own; each thing in it is a part of C4. | always signed out | the banner | C4 |  | E10, E11 |  |  |
| 2 | The title | heading | Sign in. |  | Sign in |  |  | E35 |  |  |
| 3 | The line | text | See your visits and book new ones. |  | the line |  |  | E35 |  |  |
| 4 | The refusal, C9 | message | The email or the password is wrong., above the form. | validation | the message, announced when it appears | C9 | R8 | E36 |  |  |
| 5 | Email, C8 | field | The account's email. | marked when refused | Email | C8 | R8 | E35, N3 |  |  |
| 6 | Password, C8 | field | The password, as dots. | marked when refused | Password | C8 | R8 | E35 |  |  |
| 7 | Keep me signed in on this device | field | A tick. |  | Keep me signed in on this device, a tick box |  | R8 | E35 |  |  |
| 8 | Sign in, C1 | button | The full width of the form; signs in, or refuses a wrong pair above the form. |  | Sign in | C1 | R8 | E35 |  |  |
| 9 | First visit | text | First visit? Book one and we set up your account.: Book one leads to SC4. |  | the line, with its link |  | R2 | E37 |  | SC4 |
| 10 | Forgotten your password? | link | Contact, where the patient writes to the clinic. Leads to SC11. |  | Forgotten your password? |  | R8 | E38 |  | SC11 |
| 11 | The footer, C5 | region | The row every screen ends with: the clinic's line, three pages about the clinic and the line on emergencies; each thing in it is a part of C5. |  | the footer | C5 |  | E10 |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Empty | observed | The two fields blank: the page as it opens. | E35 |  |
| Validation | observed | The refusal above the form; Email and Password marked, the email kept. | E36 |  |
| Error | likely |  |  | Sign in on a copy of the site with its accounts stopped. |
| Loading | likely |  |  | Sign in with the network slowed, on a copy of the site. |
| Success | likely |  |  | Sign in as the test patient on a copy of the site, and see that My visits opens. |
| Disabled | n/a | Sign in is always enabled; a blank field is refused as a wrong one is (R8). |  |  |
| Unauthorized | n/a | Anyone may sign in. |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Sign in, with an email or a password that is wrong | validation |  | R8 | E36 |
| validation | Sign in, with the account's email and password | SC5 | SC5 | R8 | E11, E35 |
| normal | Book one is selected | SC4 | SC4 | R2 | E37 |
| normal | Forgotten your password? is selected | SC11 | SC11 | R8 | E38 |

## Layout

| What | Must be | From |
|---|---|---|
| The form | 480 pixels wide at most | foundations |
| Sign in | the full width of the form | E35 |
