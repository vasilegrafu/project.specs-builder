---
id: SC6
name: Contact
kind: page
address: /contact
who: anyone, signed in or not
reached by: Contact in the header, C1, and in the footer, C2, from every page
---

A visitor or a patient finds the clinic's hours, its address with a map, how to get there, its phone and its email.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The hours of each day, the address, how to get there, the phone with the hours it is answered, and the email, set by the staff. | R5, R13 |  |
| Names, times, prices and hours shown are samples, not the clinic's; the clinic's own come from the staff. | R13 |  |
| Words in square brackets are the clinic's to write, through the staff area (R13); the prototype holds their place and invents none. | R13 |  |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C1 | region | The row every public screen starts with: the clinic's name, its pages, and the visitor's own links; each thing in it is a part of C1. | signed in: My bookings and Sign out in place of Sign in and Register | the banner | C1 |  | F1 |  |  |
| 2 | Contact | heading | The page's title. |  | Contact, heading level 1 |  | R5 |  |  |  |
| 3 | Opening hours | heading | The heading over the hours. |  | Opening hours, heading level 2 |  | R5 |  |  |  |
| 4 | The hours | table | The seven days, each with its hours. |  | table, 2 columns, 7 rows |  | R5 |  |  |  |
| 5 | A day | text | Monday to Sunday; it repeats. |  | the row header |  | R5 |  |  |  |
| 6 | Its hours | text | 8:00 AM – 6:00 PM, or Closed; it repeats. |  | the cell |  | R5 |  |  |  |
| 7 | Address | heading | The heading over the address. |  | Address, heading level 2 |  | R5 |  |  |  |
| 8 | The address | text | The clinic's street address, New York, NY. |  | the address |  | R5 |  |  |  |
| 9 | The map | picture | A map of where the clinic is. |  | Map of the clinic's address |  | R5 |  |  |  |
| 10 | Getting here | heading | The heading over how to get there. |  | Getting here, heading level 2 |  | R5 |  |  |  |
| 11 | How to get here, said | text | How to get there, in the clinic's words. |  | the paragraph |  | R5 |  |  |  |
| 12 | Phone and email | heading | The heading over the phone and the email. |  | Phone and email, heading level 2 |  | R5 |  |  |  |
| 13 | The phone | text | The clinic's phone, with the hours it is answered; on a phone, selected, it calls the clinic. |  | the number |  | R5 |  |  |  |
| 14 | The email | text | The clinic's email; selected, it opens the visitor's email. |  | the email |  | R5 |  |  |  |
| 15 | The page can't be shown, C8 | message | "This page can't be shown right now. Please try again in a moment, or call the clinic." | error | the message, announced when it appears | C8 |  |  |  |  |
| 16 | The site footer, C2 | region | The row every public screen ends with: the line on emergencies, Contact, Privacy and the staff's way in; each thing in it is a part of C2. |  | the footer | C2 | R11 |  |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Empty | n/a | The page's words are the clinic's, set by the staff (R13); it opens with them. |  |  |
| Loading | n/a | It opens with its words; nothing is fetched after it opens. |  |  |
| Error | added | The header, the footer and, in place of the page, "This page can't be shown right now. Please try again in a moment, or call the clinic.", element 15. |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | the staff change the hours and save | normal |  | R5 |  |
