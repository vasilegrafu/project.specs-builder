---
name: Larkfield Clinic
kind: application
status: agreed
---

Larkfield Clinic's website lets a patient book a visit with the doctor, nurse or physiotherapist of their choice, see their visits, and cancel one up to 24 hours before it starts; anyone reads the team, the opening hours and how to reach the clinic.
This specification says what the site does today, page by page, so that the new supplier building it again for March 2027 builds the same site, with the one change the practice asks for (E1, E4).

## Problem

The site's supplier closes at the end of 2026, and without a specification the new one would rebuild the site from guesses.
Today the front desk takes about 260 calls a week from patients who book or cancel a visit, and the line is busy for everyone else while it does (E2).
About 38 visits a month are missed without a word, a time someone else could have had (E3).
Both counts are the front desk's, for September 2026.

## Users

The visitor: anyone on the site who is not signed in, who reads the team, the hours and how to reach the clinic, and books a first visit with their email (U1).
The patient: one of the about 5,800 on the clinic's list, signed in, who books, sees and cancels their visits and keeps their contact details; today many of them phone the front desk to book or cancel instead (U2).
The front desk works in the practice's appointments system and not on the site; it takes the calls, the late cancellations and every change of a name or a date of birth (E8, E41).

## Journey

1. A patient opens the site, reads the team, and chooses who to see; or goes straight to Book a visit.
2. In the form they choose the doctor, nurse or physiotherapist, the day and the time, say what the visit is about, give their email, and book.
3. A day that has passed, a time not chosen or an email that is not one is refused, field by field; a day with no free time says the nearest free times; they correct it and book again.
4. The visit is booked, with its number; the details go to their email, and a text reminds them the day before.
5. Under My visits they see what is coming up and what is past, and cancel a visit up to 24 hours before it starts; later than that, they phone the front desk, as about 260 a week phone today to book or cancel.

## Non-goals

- Repeat prescriptions online and video visits: both are asked for, and both wait for the practice's new appointments system in 2028 (E5).
- The appointments system and the front desk's own work: the site ends at the visit booked, seen and cancelled (E8).
- Anything the site does not do today, but the doctor chosen from their page, R4: the rebuild adds nothing else and loses nothing (E1).

## Assumptions

- The front desk counts the calls to book or cancel, and the visits missed, the same way after launch as in September 2026. To check: ask Helen for both counts of the first full week after launch, and set them beside a week of September's.

## Release plan

| Release | Holds | Outcome |
|---|---|---|
| First | R1, R2, R3, R5, R6, R7, R8, R9, R10, R11 | the site as it runs today, built again: a patient books, sees and cancels a visit, and is reminded the day before |
| Later | R4 | a patient who books from a doctor's page finds that doctor already chosen |
