---
id: SC4
name: The team
kind: list
address: /team
who: anyone, signed in or not
reached by: Team in the header, C1
follows: FD1, FD2, FD3, FD4, FD5, FD7, FD8, FD9, FD10
---

A visitor sees the clinicians who work at NovaLife, each with their photograph, name, role and qualifications.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The clinicians who work at NovaLife now, each with their name, photograph, role and qualifications, set by the staff. | R8, R13 |  |
| Names, times, prices and hours shown are samples, not the clinic's; the clinic's own come from the staff. | R13 |  |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C1 | region | The row every public screen starts with: the clinic's name, its pages, and the visitor's own links; each thing in it is a part of C1. | signed in: My bookings and Sign out in place of Sign in and Register | the banner | C1 |  | F1 |  |  |
| 2 | Our team | heading | The page's title. |  | Our team, heading level 1 |  | R8 |  |  |  |
| 3 | A clinician | region | One clinician; the cards repeat, one for each who works at NovaLife. |  | the clinician's name, role and qualifications |  | R8 |  |  |  |
| 4 | Their photograph | picture | A photograph of the clinician. |  | Photograph of, the name |  | R8 |  |  |  |
| 5 | Their name | heading | Dr. Lee. |  | the name, heading level 2 |  | R8 |  |  |  |
| 6 | Their role | text | Physician, internal medicine. |  | the role |  | R8 |  |  |  |
| 7 | Their qualifications | text | MD; board-certified in internal medicine. |  | the qualifications |  | R8 |  |  |  |
| 8 | Nobody yet, C8 | message | "Our team will be introduced here soon." | empty | the message | C8 | R8 |  |  |  |
| 9 | The page can't be shown, C8 | message | "This page can't be shown right now. Please try again in a moment, or call the clinic." | error | the message, announced when it appears | C8 |  |  |  |  |
| 10 | The site footer, C2 | region | The row every public screen ends with: the line on emergencies, Contact, Privacy and the staff's way in; each thing in it is a part of C2. |  | the footer | C2 | R11 |  |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Empty | added | No clinician set yet: "Our team will be introduced here soon.", element 8. |  |  |
| Loading | n/a | It opens with the team; nothing is fetched after it opens. |  |  |
| Error | added | The header, the footer and, in place of the team, "This page can't be shown right now. Please try again in a moment, or call the clinic.", element 9. |  |  |
| No-results | n/a | The list is not searched or filtered. |  |  |
| Hover | added | A link darkens under the pointer, and a link of the header is underlined; a touch screen has nothing in its place; a button on the page, where there is one, is at least 44 pixels high. |  |  |
| Keyboard | added | Tab reaches the header's links, the page's links and buttons in reading order, then the footer's; the focus shows as a clear outline; Enter follows a link. |  |  |
| Mobile | added | At 375 pixels the header's pages move to a row of their own beneath the clinic's name, and every section stacks in one column. |  |  |
| Navigation | added | The page has its own address; back returns to the page before; a reload shows it as it was. |  |  |
| Permissions | stated | Anyone sees it, signed in or not; signed in, the header offers My bookings and Sign out (C1). |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | a clinician leaves and the staff remove them | normal |  | R8 |  |
