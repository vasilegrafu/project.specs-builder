---
id: SC5
name: Staff sign-in
kind: form
address: /staff/sign-in
who: anyone; only staff can get past it
reached by: any staff address while signed out; Sign out on C2
shows: R4, R23
---

A member of staff signs in to read the feedback.

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The business's name | text | [Business name], at the top of the page. |  | the business's name | C9 |  |  | Q17 |  |
| 2 | The heading | heading | Staff sign-in |  | Staff sign-in |  |  |  |  |  |
| 3 | Wrong details | message | Above the form, when the email address or password is wrong. | shown on error | Wrong email address or password | C6 | R4 |  |  |  |
| 4 | Too many tries | message | Above the form, when the limit on failed sign-ins is reached. | shown on blocked | Too many tries | C6 | R4 |  | Q16 |  |
| 5 | Email address | field | The member of staff's email address. |  | Email address | C4 | R4 |  |  |  |
| 6 | Password | field | Their password, hidden as it is typed. |  | Password | C4 | R4 |  |  |  |
| 7 | Sign in | button | Signs in. Leads to SC6. | signing in | Sign in | C3 | R4 |  |  | SC6 |
| 8 | Forgotten password | text | Says to ask the developer. |  | the line |  | R4 |  |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| empty | added | The form with nothing filled in. |  |  |
| validation | added | Each empty field asks for itself. |  |  |
| error | added | Wrong details, above the form; the password is cleared. |  |  |
| blocked | added | Too many tries, above the form; nothing can be signed in until the limit has passed. |  |  |
| loading | added | Sign in cannot be pressed again. |  |  |
| success | n/a | n/a: it leads straight to SC6. |  |  |
| disabled | n/a | n/a: the form is always open. |  |  |
| unauthorized | n/a | n/a: this is where anyone not signed in is sent. |  |  |
| hover | added | The fields and buttons mark themselves under the pointer; a touch screen has nothing in its place. |  |  |
| keyboard | added | Tab reaches the fields in order, then the button; the focus always shows; Enter sends. |  |  |
| mobile | added | At 375 pixels everything stands in one column at full width. |  |  |
| navigation | added | Back leaves the page; a reload keeps nothing that was typed. |  |  |
| permissions | added | Anyone sees the same page, and only staff can get past it. |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Sign in is pressed with the right details | SC6 | SC6 | R4 |  |
| normal | Sign in is pressed with wrong details | error |  | R4 |  |
| error | The limit on failed sign-ins is reached | blocked |  | R4 |  |
