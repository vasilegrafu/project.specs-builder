# The meaning of Larkfield Clinic's site

- **Role:** meaning
- **Read:** the findings E1 to E61 and the contradictions X1 and X2; the usage analysis

## Terms

| Term | Means | Also called | Findings |
|---|---|---|---|
| visit | a time booked with one of the team | appointment, in the brief's way of speaking | E24, E59 |
| the team | the six who see patients: four doctors, a nurse, a physiotherapist | the doctors, on the menu | E12 |
| usual times | the times a visit with one of the team starts on a working day | | E14 |
| free time | a usual time no visit holds yet | | E14, E23 |
| coming up | a visit booked that has not taken place | | E26 |
| front desk | the clinic's reception, where the calls are taken | | E41, E47 |

## Entities

| Entity | What it is to a user | Fields | Findings |
|---|---|---|---|
| visit | what they booked, and where it stands | number, with, when, about, where, status | E24, E26, E28 |
| one of the team | who they see | name, role, days, what they look after, usual times | E12, E13 |
| patient | who they are to the clinic | full name, date of birth, email, phone | E40 |

## Lifecycles

| Entity | From | Event | To | Findings |
|---|---|---|---|---|
| visit | booked | the visit takes place | attended | E31 |
| visit | booked | the patient cancels it, up to 24 hours before | cancelled | E30, E33 |
| patient | none | a first visit is booked | patient | E37 |

## Rules

| Rule | Except | Findings |
|---|---|---|
| a visit is booked from tomorrow to three months ahead | | E17, E21 |
| a time holds one visit; a day with no free time is refused | | E23, E33 |
| a visit is cancelled on the site up to 24 hours before | later, by calling | E30 |
| a name and a date of birth change only at the front desk | | E41 |
| what a visit is about is up to 200 characters, never an emergency | | E18 |
| messages only about visits: confirmation, reminder, note | | E43 |

## Roles

| Role | Who | Findings |
|---|---|---|
| visitor | anyone not signed in | E6, E10 |
| patient | signed in to their account | E6, E11 |

## Unknowns

- What a visit less than 24 hours away shows: no finding says (E30).
- How a first visit's account gets its password: no finding says (E37).
- Whether a visit missed without a word has a status of its own: the site shows booked, attended and cancelled alone (E3, E28).
