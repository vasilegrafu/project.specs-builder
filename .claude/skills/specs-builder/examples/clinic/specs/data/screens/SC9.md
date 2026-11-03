---
id: SC9
name: Signed out
kind: page
address: /signed-out
who: anyone, once signed out
reached by: Sign out in the header, signed in
follows: FD1, FD2, FD3, FD4, FD5, FD7, FD8, FD9, FD10
---

A patient who signed out learns that they are, and goes on from there.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| Nothing but the words: the patient is signed out. | R9 |  |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C4 | region | The row every screen starts with: the mark, the clinic's four links, then the patient's own; each thing in it is a part of C4. | always signed out | the banner | C4 |  | E10, E11 |  |  |
| 2 | The title | heading | You are signed out. |  | You are signed out |  | R9 | E39 |  |  |
| 3 | The way on | text | Thanks for visiting. Sign in again or go to the home page.: Sign in again leads to SC8, the home page to SC1. |  | the line, with two links |  | R9 | E39 |  | SC8 |
| 4 | The footer, C5 | region | The row every screen ends with: the clinic's line, three pages about the clinic and the line on emergencies; each thing in it is a part of C5. |  | the footer | C5 |  | E10 |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Empty | n/a | The page is its own words; there is nothing for it to be empty of. |  |  |
| Loading | n/a | It arrives whole, with nothing to wait for. |  |  |
| Error | n/a | It asks nothing of a server once it is open. |  |  |
| Hover | observed | a link of the header turns green and is underlined. | E51, E61 |  |
| Keyboard | observed | Tab reaches the header's links, Sign in again and the home page; the focus shows on each. | E55 |  |
| Mobile | observed | At 375 pixels the line wraps under the title. Seen in evidence/captures/site/shots/V19-375.jpg. |  |  |
| Navigation | likely |  |  | Sign out on a copy of the site, go back, and see whether My visits shows again. |
| Permissions | observed | Anyone reaches it; the header is the visitor's. | E10 |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Sign in again is selected | SC8 | SC8 | R9 | E39 |
| normal | The home page is selected | SC1 | SC1 | R9 | E39 |
