---
id: SC1
name: The home page
kind: page
address: /
who: anyone, signed in or not
reached by: the site's address; the mark in the header, from every screen; the home page on SC9
---

Anyone sees when the clinic is open today, and goes to book a visit or to meet the team.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The hours of the day it is, from the clinic's opening hours. | R11 |  |
| Three of the team, with their role and days (N2, R1); the clinic's news, written by the practice. | R1 | N2 |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C4 | region | The row every screen starts with: the mark, the clinic's four links, then the patient's own; each thing in it is a part of C4. | signed in: My visits, the first name and Sign out in place of Sign in and Book a visit | the banner | C4 |  | E10, E11 |  |  |
| 2 | The kicker | text | A FAMILY PRACTICE IN LARKFIELD SINCE 1998, over the title. |  | A family practice in Larkfield since 1998 |  |  | E9 |  |  |
| 3 | The welcome | heading | See a doctor this week. |  | See a doctor this week |  |  | E9 |  |  |
| 4 | The line | text | Book a visit with the doctor or nurse of your choice, see your visits, and cancel one when plans change. |  | the line |  |  | E9 |  |  |
| 5 | Book a visit, C1 | link | Large. Leads to SC4. |  | Book a visit | C1 | R2 |  |  | SC4 |
| 6 | Meet the doctors, C2 | link | Large. Leads to SC2. |  | Meet the doctors | C2 | R1 |  |  | SC2 |
| 7 | Open today | heading | Open today; Closed today on a Sunday. | closed on a Sunday | Open today |  | R11 | E48 |  |  |
| 8 | The day's hours | text | The hours of the day it is, large; none on a Sunday. | hidden on a Sunday | the hours |  | R11 | E45, E48 |  |  |
| 9 | Three days | table | Monday, Tuesday and Wednesday with their hours. |  | a table of three rows |  | R11 | E45 |  |  |
| 10 | A day | text | The day of the week the row is. |  | the day |  |  | E45 |  |  |
| 11 | Its hours | text | When the clinic opens and closes that day. |  | the hours |  | R11 | E45 |  |  |
| 12 | All opening hours | link | To every day of the week. Leads to SC11. |  | All opening hours |  | R11 |  |  | SC11 |
| 13 | The doctors | heading | The heading over three of the team. |  | The doctors |  |  | E12 |  |  |
| 14 | Three of the team, cards of C6 | list | The first three of the team, three to a row. Each card's parts are C6's. |  | Three of the team | C6 | R1 | E12, N2 |  |  |
| 15 | All six of the team | link | To the whole team. Leads to SC2. |  | All six of the team |  | R1 |  |  | SC2 |
| 16 | News | heading | The heading over the news. |  | News |  |  | E9 |  |  |
| 17 | A piece of news | text | Its date, its title and a line; three, the newest first. |  | the date, the title and the line |  |  | E9 |  |  |
| 18 | The footer, C5 | region | The row every screen ends with: the clinic's line, three pages about the clinic and the line on emergencies; each thing in it is a part of C5. |  | the footer | C5 |  | E10 |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Empty | n/a | The page is the clinic's own words and its team; there is nothing for it to be empty of. |  |  |
| Loading | n/a | It arrives whole, with nothing to wait for. |  |  |
| Error | n/a | It asks nothing of a server once it is open. |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Book a visit is selected | SC4 | SC4 | R2 | E9 |
| normal | Meet the doctors, or All six of the team, is selected | SC2 | SC2 | R1 | E9 |
| normal | A name is selected | SC3 | SC3 | R1 | E12 |
| normal | All opening hours is selected | SC11 | SC11 | R11 | E45 |

## Variants

| What differs, and for whom | About |
|---|---|
| Signed in, the header offers My visits, the first name and Sign out, parts of C4. | E11, C4 |

## Layout

| What | Must be | From |
|---|---|---|
| The welcome and Open today | side by side above 800 pixels, the welcome the wider; one above the other below | foundations |
| The cards | three to a row, two under 800 pixels, one under 480 | foundations |
