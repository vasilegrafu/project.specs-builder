---
id: SC2
name: The team
kind: list
address: /doctors/
who: anyone, signed in or not
reached by: Doctors in the header, from every screen; Meet the doctors and All six of the team on SC1; Doctors in the crumbs of SC3
---

Anyone sees who works at the clinic, and opens one of them.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The six of the team, each with their picture, name, role and working days. | R1 | N2 |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C4 | region | The row every screen starts with: the mark, the clinic's four links, then the patient's own; each thing in it is a part of C4. | signed in: My visits, the first name and Sign out in place of Sign in and Book a visit | the banner | C4 |  | E10, E11 |  |  |
| 2 | The title | heading | The doctors. |  | The doctors |  |  | E12 |  |  |
| 3 | The line | text | Six of us: four doctors, a nurse and a physiotherapist. |  | the line |  |  | E12 |  |  |
| 4 | The team, cards of C6 | list | The six of the team, three to a row. Each card's parts are C6's. |  | The team | C6 | R1 | E12, N2 |  |  |
| 5 | The footer, C5 | region | The row every screen ends with: the clinic's line, three pages about the clinic and the line on emergencies; each thing in it is a part of C5. |  | the footer | C5 |  | E10 |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Empty | n/a | The clinic always has its team; the list is the practice's own. |  |  |
| Loading | n/a | It arrives whole, with nothing to wait for. |  |  |
| Error | n/a | It asks nothing of a server once it is open. |  |  |
| No-results | n/a | The list is neither searched nor filtered. |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | A name is selected | SC3 | SC3 | R1 | E12 |
