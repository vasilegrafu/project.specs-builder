---
id: SC4
name: Book a visit
kind: form
address: /book; /book?doctor={slug} opens it with that one chosen (R4)
who: anyone: a visitor books a first visit with their email, and an account is set up for it (E37)
reached by: Book a visit in the header, from every screen; Book a visit on SC1; Book a visit with on SC3; Book another with on SC6; Book another visit on SC5 and SC7; Book one on SC8
follows: FD1, FD2, FD3, FD4, FD5, FD7, FD8, FD9, FD10
---

Anyone books a visit with the one of the team they choose, on a day and at a time that is free, and sees it booked.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The one to see, the day, the time, what it is about and the email, sent to book the visit. | R2 | N1 |
| The usual times of the one chosen, which the Time offers (N2, B2); which of them are free on the day is known only once the form is sent. |  | Q1, N2, B2 |
| The visit booked: its number, with whom, when, what about and where. | R2 | N1 |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C4 | region | The row every screen starts with: the mark, the clinic's four links, then the patient's own; each thing in it is a part of C4. | signed in: My visits, the first name and Sign out in place of Sign in and Book a visit | the banner | C4 |  | E10, E11 |  |  |
| 2 | The title | heading | Book a visit. | not in success | Book a visit |  |  | E16 |  |  |
| 3 | The line | text | Choose who you want to see and when. We confirm by email. | not in success | the line |  |  | E16 |  |  |
| 4 | The refusal, C9 | message | Three things need a look before the visit can be booked.: how many fields need a look, above the form. | validation | the message, announced when it appears | C9 | R3 | E20 |  |  |
| 5 | The day full, C9 | message | Dr Tom Hale has no free time on 20 October 2026. The nearest free times are on 23 October: 10:30 and 15:00. | full | the message, announced when it appears | C9 | R3 | B2, E23 | Q1 |  |
| 6 | Who and when | heading | The legend over the one to see, the day and the time. |  | Who and when |  |  | E16 |  |  |
| 7 | Doctor or nurse, C8 | field | Choose, then the six of the team with their role; chosen already when opened from SC3. |  | Doctor or nurse | C8 | R2, R4 | E16, N2 |  |  |
| 8 | Day, C8 | field | A day from tomorrow to three months ahead. | marked when refused | Day | C8 | R3 | B1, E17 |  |  |
| 9 | Why the day is refused | message | "That day has passed. Choose a day from tomorrow on.", under the field, when the form is refused. | validation | the reason, read with the field |  | R3 | B1, E21 |  |  |
| 10 | Time, C8 | field | Choose, then the usual times of the one chosen. | marked when refused | Time | C8 | R2 | B2, E19 |  |  |
| 11 | Why the time is refused | message | "Choose a time.", under the field, when the form is refused. | validation | the reason, read with the field |  | R3 | E22 |  |  |
| 12 | About the visit | heading | The legend over what it is about and the email. |  | About the visit |  |  | E16 |  |  |
| 13 | What is it about?, C8 | field | Up to 200 characters. |  | What is it about? | C8 |  | B5, E18 |  |  |
| 14 | The hint | text | Up to 200 characters. Not for emergencies: call 999. |  | read with the field |  |  | B5, E18 |  |  |
| 15 | Your email, C8 | field | Where the details go. | marked when refused | Your email | C8 | R2 | E16 |  |  |
| 16 | Why the email is refused | message | "That is not an email address.", under the field, when the form is refused. | validation | the reason, read with the field |  | R3 | E22 |  |  |
| 17 | Book the visit, C1 | button | Books the visit; a field wrong is refused, and a day full is said, above the form. |  | Book the visit | C1 | R2, R3 | E16 |  |  |
| 18 | Cancel | link | Nothing booked. Leads to SC1. |  | Cancel |  |  | E16 |  | SC1 |
| 19 | Booked | heading | Your visit is booked. | success | Your visit is booked |  | R2 | E24 |  |  |
| 20 | The visit's number | text | VISIT LC-2041. | success | Visit LC-2041 |  |  | E59, N1 |  |  |
| 21 | The visit's facts | region | With, When, About and Where, each with its value. | success | the visit's facts |  |  | E24, N1 |  |  |
| 22 | A fact's name | text | With, When, About or Where: what the value beside it is. | success | the name |  |  | N1 |  |  |
| 23 | With whom | text | The one chosen, with what they are. | success | Dr Amara Okafor, general practitioner |  |  | E24, N1, N2 |  |  |
| 24 | When | text | The day and the time chosen. | success | the day and time |  |  | E24, N1 |  |  |
| 25 | About what | text | What the visit is about, as written. | success | the reason |  |  | E24, N1 |  |  |
| 26 | Where | text | The clinic's address. | success | the address |  |  | E24, E46 |  |  |
| 27 | The email sent | text | We have sent the details to the email; arrive five minutes early. | success | the line |  |  | B6, E25 |  |  |
| 28 | My visits, C1 | link | To the patient's visits. Leads to SC5. | success | My visits | C1 | R5 |  |  | SC5 |
| 29 | See this visit, C2 | link | To the visit just booked. Leads to SC6. | success | See this visit | C2 | R5 |  |  | SC6 |
| 30 | The footer, C5 | region | The row every screen ends with: the clinic's line, three pages about the clinic and the line on emergencies; each thing in it is a part of C5. |  | the footer | C5 |  | E10 |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Validation | observed | The refusal above the form; each refused field with a red edge and its reason under it; what was typed kept. | E20 |  |
| Error | likely |  |  | Send the form on a copy of the site with the appointments system stopped. |
| Loading | likely |  |  | Send the form with the network slowed, on a copy of the site. |
| Success | observed | The visit booked in place of the form: its number, its facts, where the details went. | E24 |  |
| Disabled | n/a | Book the visit is always enabled; what is wrong is said once it is selected (R3). |  |  |
| Unauthorized | n/a | Anyone may book; a first visit sets up the account (E37). |  |  |
| Full | observed | The day full above the form, which keeps what was chosen. | E23 |  |
| Hover | observed | A primary button darkens under the pointer, C1; a secondary button takes a pale green ground, C2; a link of the header turns green and is underlined. | E51, E61 |  |
| Keyboard | observed | Tab reaches the header's links, Doctor or nurse, Day, Time, What is it about?, Your email, Book the visit and Cancel, in that order; the focus shows on each. | E55 |  |
| Mobile | observed | At 375 pixels the form takes the full width, each field under its label. Seen in evidence/captures/site/shots/V7-375.jpg. |  |  |
| Navigation | likely |  |  | Book on a copy of the site, go back from the visit booked, and see whether the form is sent again. |
| Permissions | observed | Anyone reaches it, signed in or not. | E10, E37 |  |
| Empty | observed | The form blank, nobody chosen: the page as it opens from the header. Seen in evidence/captures/site/shots/V6-1280.jpg. |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Book the visit, with a field wrong | validation |  | R3 | E20, E22 |
| normal | Book the visit, on a day with no free time | full |  | R3 | E23 |
| validation | Book the visit, every field right | success |  | R2 | E24 |
| full | Book the visit, with a free time | success |  | R2 | E24 |
| normal | Cancel is selected | SC1 | SC1 | R2 | E16 |
| success | My visits is selected | SC5 | SC5 | R5 | E24 |
| success | See this visit is selected | SC6 | SC6 | R5 | E24 |

## Variants

| What differs, and for whom | About |
|---|---|
| Opened from SC3, the one of that page is chosen in Doctor or nurse, and the Time offers their usual times. | R4, SC3 |
| Signed in, the header offers My visits, the first name and Sign out, parts of C4 (E11). The visit booked shows so, the account set up. | E37, C4, E11 |

## Layout

| What | Must be | From |
|---|---|---|
| The form | 640 pixels wide at most, on white, with the banners the same width above it | E20 |
| The visit booked | 640 pixels wide at most | foundations |
