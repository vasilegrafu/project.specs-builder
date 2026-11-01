---
id: SC7
name: Privacy notice
kind: page
address: /privacy
who: anyone, signed in or not
reached by: Privacy in the footer, C2, from every page; the link in booking, SC8 and SC10
---

A visitor or a patient reads what the website keeps about them, why, who reads it and for how long.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| What an account and a booking keep, which the decisions fix: first and last name, date of birth, email, phone, and the bookings. | R10, R16 |  |
| Why it is kept, who reads it and for how long: what the law asks is open, Q11. | R10 | Q11 |
| Words in square brackets are the clinic's to write, through the staff area (R13); the prototype holds their place and invents none. | R13 |  |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C1 | region | The row every public screen starts with: the clinic's name, its pages, and the visitor's own links; each thing in it is a part of C1. | signed in: My bookings and Sign out in place of Sign in and Register | the banner | C1 |  | F1 |  |  |
| 2 | Privacy | heading | The page's title. |  | Privacy, heading level 1 |  | R10 |  | Q11 |  |
| 3 | What we keep | heading | The first part. |  | What we keep, heading level 2 |  | R10 |  | Q11 |  |
| 4 | What we keep, said | text | Your first and last name, date of birth, email and phone, and your bookings. No medical details are asked for or kept. |  | the paragraph |  | R10 |  | Q11 |  |
| 5 | Why | heading | The second part. |  | Why, heading level 2 |  | R10 |  | Q11 |  |
| 6 | Why, said | text | To book your appointments, and to reach you about them. |  | the paragraph |  | R10 |  | Q11 |  |
| 7 | Who reads it | heading | The third part. |  | Who reads it, heading level 2 |  | R10 |  | Q11 |  |
| 8 | Who reads it, said | text | NovaLife's staff: the front desk, the administrator, and the doctor you book with. |  | the paragraph |  | R10 |  | Q11 |  |
| 9 | For how long | heading | The fourth part. |  | For how long, heading level 2 |  | R10 |  | Q11 |  |
| 10 | For how long, said | text | How long it is kept, as the law asks. |  | the paragraph |  | R10 |  | Q11 |  |
| 11 | The page can't be shown, C8 | message | "This page can't be shown right now. Please try again in a moment, or call the clinic." | error | the message, announced when it appears | C8 |  |  |  |  |
| 12 | The site footer, C2 | region | The row every public screen ends with: the line on emergencies, Contact, Privacy and the staff's way in; each thing in it is a part of C2. |  | the footer | C2 | R11 |  |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Empty | n/a | The page's words are the clinic's, set by the staff (R13); it opens with them. |  |  |
| Loading | n/a | It opens with its words; nothing is fetched after it opens. |  |  |
| Error | added | The header, the footer and, in place of the page, "This page can't be shown right now. Please try again in a moment, or call the clinic.", element 11. |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | the staff change the notice and save | normal |  | R13 |  |
