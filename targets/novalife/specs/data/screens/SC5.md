---
id: SC5
name: Becoming a patient
kind: page
address: /new-patients
who: anyone, signed in or not
reached by: New patients in the header, C1
follows: FD1, FD2, FD3, FD4, FD5, FD8, FD9, FD10
---

A visitor finds out, on one page, how to become a patient, what happens at the first visit and what to bring to it.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The three answers, in the clinic's words, set by the staff. | R9, R13 |  |
| How to become a patient follows the decisions: any appointment type is booked directly, with an account, and paid by the patient. | R6, R16, R7 |  |
| Wording beyond what the brand and the requirements fix is a draft, proposed on 2026-10-20 for the clinic to replace through the staff area (R13); what it may say of health and longevity waits on Q12. | R13 | Q12 |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C1 | region | The row every public screen starts with: the clinic's name, its pages, and the visitor's own links; each thing in it is a part of C1. | signed in: My bookings and Sign out in place of Sign in and Register | the banner | C1 |  | F1 |  |  |
| 2 | Becoming a patient | heading | The page's title. |  | Becoming a patient, heading level 1 |  | R9 |  |  |  |
| 3 | How to become a patient | heading | The first question. |  | heading level 2 |  | R9 |  |  |  |
| 4 | How, said | text | Book your first appointment online: choose a service and an appointment type, then a free time, and create your account as you book. No referral or earlier consultation is needed. |  | the paragraph |  | R9 |  |  |  |
| 5 | See the services | link | The services, to choose one. Leads to SC2. |  | See the services |  | R9 |  |  | SC2 |
| 6 | What happens at the first visit | heading | The second question. |  | heading level 2 |  | R9 |  |  |  |
| 7 | The first visit, said | text | What happens at the first visit, in a draft of the clinic's words. |  | the paragraph |  | R9 |  |  |  |
| 8 | What to bring | heading | The third question. |  | heading level 2 |  | R9 |  |  |  |
| 9 | What to bring, said | text | What to bring, in a draft of the clinic's words. |  | the paragraph |  | R9 |  |  |  |
| 10 | Book your first appointment, C6 | button | Opens booking. Leads to SC8. |  | Book your first appointment | C6 | R9 |  |  | SC8 |
| 11 | The page can't be shown, C8 | message | "This page can't be shown right now. Please try again in a moment, or call the clinic." | error | the message, announced when it appears | C8 |  |  |  |  |
| 12 | The site footer, C2 | region | The row every public screen ends with: the line on emergencies, Contact, Privacy and the staff's way in; each thing in it is a part of C2. |  | the footer | C2 | R11 |  |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Empty | n/a | The page's words are the clinic's, set by the staff (R13); it opens with them. |  |  |
| Loading | n/a | It opens with its words; nothing is fetched after it opens. |  |  |
| Error | added | The header, the footer and, in place of the page, "This page can't be shown right now. Please try again in a moment, or call the clinic.", element 11. |  |  |
| Hover | added | A link darkens under the pointer, and a link of the header is underlined; a touch screen has nothing in its place; a button on the page, where there is one, is at least 44 pixels high. |  |  |
| Keyboard | added | Tab reaches the header's links, the page's links and buttons in reading order, then the footer's; the focus shows as a clear outline; Enter follows a link. |  |  |
| Mobile | added | At 375 pixels the header's pages move to a row of their own beneath the clinic's name, and every section stacks in one column. |  |  |
| Navigation | added | The page has its own address; back returns to the page before; a reload shows it as it was. |  |  |
| Permissions | stated | Anyone sees it, signed in or not; signed in, the header offers My bookings and Sign out (C1). |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | See the services is chosen | SC2 | SC2 | R9 |  |
| normal | Book your first appointment is chosen | SC8 | SC8 | R9 |  |
