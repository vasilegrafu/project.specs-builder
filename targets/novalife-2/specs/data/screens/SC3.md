---
id: SC3
name: About NovaLife
kind: page
address: /about
who: anyone, signed in or not
reached by: About in the header, C1; What makes NovaLife different on SC1
---

A visitor reads NovaLife's vision and ambition, with their limit, and how it differs from the traditional approach, point by point.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The vision, the mission and the ambition, which the brand and R4 fix. | R4, R13 |  |
| The five comparisons, as R3 names them. | R3 |  |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C1 | region | The row every public screen starts with: the clinic's name, its pages, and the visitor's own links; each thing in it is a part of C1. | signed in: My bookings and Sign out in place of Sign in and Register | the banner | C1 |  | F1 |  |  |
| 2 | About NovaLife | heading | The page's title. |  | About NovaLife, heading level 1 |  | R4 |  | Q12 |  |
| 3 | Our vision | heading | Our vision: The Future of Health. |  | Our vision, heading level 2 |  | R4 |  | Q12 |  |
| 4 | The mission | text | Help people understand their health, act earlier, and stay healthier for longer. |  | the mission |  | R4 |  | Q12 |  |
| 5 | The ambition | text | To push the boundaries of healthy human longevity through evidence-based prevention, early detection and better management of established health risks. |  | the ambition |  | R4 |  | Q12 |  |
| 6 | The limit of the ambition | text | "Immortality is an aspirational idea, not a current medical capability or a promise NovaLife Clinic makes." |  | the line |  | R4 |  | Q12 |  |
| 7 | How NovaLife is different | heading | The heading over the five comparisons. |  | How NovaLife is different, heading level 2 |  | R3 |  |  |  |
| 8 | The comparisons | table | Five rows, the traditional approach beside NovaLife's. |  | table, 2 columns, 5 rows |  | R3 |  |  |  |
| 9 | A column's name | text | The traditional approach; NovaLife. |  | the column header |  | R3 |  |  |  |
| 10 | The traditional approach | text | The traditional approach, in one of the five rows; it repeats. |  | the cell |  | R3 |  |  |  |
| 11 | NovaLife's | text | NovaLife's approach, beside it; it repeats. |  | the cell |  | R3 |  |  |  |
| 12 | Technology supports | text | "Technology supports medical professionals; it does not replace their judgment." |  | the line |  | R3 |  |  |  |
| 13 | Book an appointment, C6 | button | Opens booking. Leads to SC8. |  | Book an appointment | C6 |  | F1 |  | SC8 |
| 14 | The page can't be shown, C8 | message | "This page can't be shown right now. Please try again in a moment, or call the clinic." | error | the message, announced when it appears | C8 |  |  |  |  |
| 15 | The site footer, C2 | region | The row every public screen ends with: the line on emergencies, Contact, Privacy and the staff's way in; each thing in it is a part of C2. |  | the footer | C2 | R11 |  |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Empty | n/a | The page's words are the clinic's, set by the staff (R13); it opens with them. |  |  |
| Loading | n/a | It opens with its words; nothing is fetched after it opens. |  |  |
| Error | added | The header, the footer and, in place of the page, "This page can't be shown right now. Please try again in a moment, or call the clinic.", element 14. |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Book an appointment is chosen | SC8 | SC8 | R6 |  |
