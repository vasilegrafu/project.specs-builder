---
id: SC3
name: One of the team
kind: detail
address: /doctors/{slug}
who: anyone, signed in or not
reached by: a name on SC2 or SC1; the name of the one a visit is with, on SC6
follows: FD1, FD2, FD3, FD4, FD5, FD7, FD8, FD9, FD10
---

Anyone reads about one of the team, their days and usual times, and books a visit with them.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| One of the team: picture, name, role, days, what they look after, usual times. | R1 | N2 |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C4 | region | The row every screen starts with: the mark, the clinic's four links, then the patient's own; each thing in it is a part of C4. | signed in: My visits, the first name and Sign out in place of Sign in and Book a visit | the banner | C4 |  | E10, E11 |  |  |
| 2 | A crumb | link | Home, which leads to SC1, then Doctors, which leads to SC2; then the name, which leads nowhere. | the last one is the page itself | You are here |  |  | E13 |  | SC1, SC2 |
| 3 | The picture | picture | A round picture, 160 pixels, with the initials. |  | nothing: it is decoration |  |  | E13, N2 |  |  |
| 4 | The name | heading | Dr Amara Okafor; for the nurse, Sam Whitfield. |  | the name |  |  | E13, E15, N2 |  |  |
| 5 | Role and days | text | General practitioner · Monday to Thursday. |  | the line |  |  | E13, N2 |  |  |
| 6 | What they look after | text | One or two sentences of their own. |  | the words |  |  | E13, N2 |  |  |
| 7 | Book a visit with, C1 | link | Book a visit with Okafor: a doctor by the surname, any other by the first name, Book a visit with Sam; opens the form with that one chosen. Leads to SC4. |  | Book a visit with Okafor | C1 | R4 | E15 |  | SC4 |
| 8 | Usual times | heading | The heading over the times. |  | Usual times |  |  | E14, N2 |  |  |
| 9 | Which are free | text | The times a visit starts on a working day; which are free shows when you book. |  | the line |  |  | B2, E14 |  |  |
| 10 | The times | list | The usual times as chips, earliest first. |  | a list of times |  |  | B2, E14, E57, N2 |  |  |
| 11 | A time | text | A time a visit starts, a chip; 08:30 or 14:00. |  | the time |  |  | B2, E14 |  |  |
| 12 | The footer, C5 | region | The row every screen ends with: the clinic's line, three pages about the clinic and the line on emergencies; each thing in it is a part of C5. |  | the footer | C5 |  | E10 |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Loading | n/a | It arrives whole, with nothing to wait for. |  |  |
| Error | n/a | It asks nothing of a server once it is open. |  |  |
| Not-found | likely |  |  | Open /doctors/no-one.html on a copy of the site, and see what shows. |
| Unauthorized | n/a | Anyone may read about the team. |  |  |
| Hover | observed | A primary button darkens under the pointer, C1; a link of the header turns green and is underlined. | E51, E61 |  |
| Keyboard | observed | Tab reaches the header's links, the crumbs, Book a visit with, then the footer; the focus shows on each. | E55 |  |
| Mobile | observed | At 375 pixels the picture stands above the name. Seen in evidence/captures/site/shots/V4-375.jpg. |  |  |
| Navigation | likely |  |  | Open a page of the team by its address, reload it, and go back. |
| Permissions | observed | Anyone reaches it, signed in or not. | E10 |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Book a visit with is selected | SC4 | SC4 | R4 | E15 |
| normal | Doctors, in the crumbs | SC2 | SC2 | R1 | E13 |

## Variants

| What differs, and for whom | About |
|---|---|
| One of the team who is not a doctor, the nurse or the physiotherapist: the button names them by their first name, "Book a visit with Sam". | E15 |
