# The usage of Larkfield Clinic's site

- **Role:** usage
- **Read:** the findings E9 to E61; the captures V1 and V3 to V24 of S2 and their inventory; their screenshots at 1280 and 375 pixels

## Screens

| Screen | Kind | Views | What the user comes here to do | Findings |
|---|---|---|---|---|
| the home page | page | V1 | see when the clinic is open, and go to booking or the team | E9, E48 |
| the doctors | list | V3 | see who is in the team | E12 |
| one of the team | detail | V4, V5 | read about one of them, and book with them | E13, E15 |
| book a visit | form | V6, V7, V8, V9 | book a visit, and see it booked | E16, E20, E23, E24 |
| my visits | list | V10, V11 | see the visits coming up and the past ones | E26, E27 |
| a visit | detail | V12, V13, V14 | see one visit, and cancel it while it is coming up | E29, E31, E32 |
| cancel a visit | dialog | V15, V16 | confirm the cancelling, and see it done | E33, E34 |
| sign in | form | V17, V18 | sign in | E35, E36 |
| signed out | page | V19 | learn they are signed out | E39 |
| my account | form | V20 | keep their email and phone | E40 |
| about the clinic | page | V21, V22, V23 | read the hours, how to reach the clinic, and what it keeps | E45, E46, E43 |

## Not screens

| View | Why |
|---|---|
| V2 | the home page under its file name, not captured: it is V1 |
| V24 | the server's own page for an address the site does not have, outside the site's frame |

## Navigation

| From | How | To | Findings |
|---|---|---|---|
| any screen | the mark, Doctors, Book a visit, Opening hours, Contact and Sign in, in the header | the home page, the doctors, book a visit, about the clinic, sign in | E10 |
| any screen, signed in | My visits, the first name and Sign out, in the header | my visits, my account, signed out | E11 |
| the doctors | a name | one of the team | E12 |
| one of the team | Book a visit with | book a visit | E15 |
| my visits | a visit's number | a visit | E26 |
| a visit | Cancel this visit | cancel a visit | E29 |

## Components

| Component | Seen in | Variants and states seen | Findings |
|---|---|---|---|
| the site header | every view | signed out; signed in | E10, E11 |
| the footer | every view | one | E10 |
| the primary button | every view | at rest; darker under the pointer | E50, E51 |
| the secondary button | V1, V10, V12, V15 | at rest; pale green under the pointer | E60, E61 |
| the danger button | V12, V15 | at rest; filled red under the pointer | E54 |
| the team's card | V1, V3 | one | E12 |
| the visit's status | V10, V12, V13, V14 | booked, attended, cancelled | E28 |
| a field with its message | V7, V18 | at rest; refused, with its reason | E21, E22 |
| the banner above a form | V7, V8, V18 | a refusal; a notice of a day with no free time | E20, E23, E53 |

## Layouts

| Screen | Regions, and what is in each | At 768 | At 375 | Findings |
|---|---|---|---|---|
| the home page | the header; the welcome beside Open today; three of the team; the news | the welcome above Open today, two cards to a row | one column | E9 |
| my visits | the header; Coming up; Past visits | the same | each visit a block of lines | E26, E56 |

## Entry points

| Entry | Who comes in there | What they find | Findings |
|---|---|---|---|
| the site's address | anyone | the home page | E9 |
| a doctor's page, from a search engine | anyone | one of the team | E13 |
| sign in | a patient | my visits, once signed in | E35 |

## Goals

| User | What they come to get done | Findings |
|---|---|---|
| the visitor | find when the clinic is open and who works there, and book a first visit | E9, E12, E37 |
| the patient | book, see and cancel their visits | E16, E26, E33 |

## Flows

### Book a visit: from the home page to a visit booked

- **User:** the visitor, or the patient
- **Goal:** a visit booked

| Step | Where | The user does | The product shows | Findings |
|---|---|---|---|---|
| 1 | the home page, the doctors, one of the team | chooses who to see | book a visit | E9, E15 |
| 2 | book a visit | fills the form and sends it | the visit booked | E16, E24 |

Branches:
- at step 2, if a field is wrong: each field says why (E20)
- at step 2, if the day has no free time: the nearest free times (E23)

### Cancel a visit: from my visits to the visit cancelled

- **User:** the patient
- **Goal:** a visit cancelled, its time freed

| Step | Where | The user does | The product shows | Findings |
|---|---|---|---|---|
| 1 | my visits | opens a visit coming up | a visit | E26, E29 |
| 2 | a visit | Cancel this visit | cancel a visit | E33 |
| 3 | cancel a visit | Cancel the visit | the visit cancelled | E34 |

Branches:
- at step 3, Keep it: back to the visit (E33)
- less than 24 hours before: call the clinic (E30)

## Decisions

| Where | What the user decides | The options | Findings |
|---|---|---|---|
| book a visit | who, which day, which time | the six of the team; tomorrow to three months ahead; the times | E16, E17 |
| cancel a visit | whether to cancel | Cancel the visit, or Keep it | E33 |

## States

| Screen or flow step | State | Status | Evidence | Investigation |
|---|---|---|---|---|
| book a visit | validation | observed | E20 | |
| book a visit | full | observed | E23 | |
| book a visit | success | observed | E24 | |
| my visits | empty | observed | E27 | |
| a visit | attended | observed | E31 | |
| a visit | cancelled | observed | E32 | |
| sign in | validation | observed | E36 | |
| a visit | less than 24 hours away | likely | | open a visit booked for tomorrow on a copy of the site |

## Permissions

| Who | May | May not, and what they then see | Findings |
|---|---|---|---|
| a visitor | read the site, book a first visit with their email | my visits and my account: sign in first | E10, E37 |
| a patient | book, see and cancel their visits, change their email and phone | change their name or date of birth: the front desk does | E11, E41 |
