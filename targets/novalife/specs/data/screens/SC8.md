---
id: SC8
name: Choose a time
kind: form
address: /book; /book?type={type} opens it with that type chosen
who: anyone: signing in is asked once a time is chosen (R6)
reached by: the booking buttons of SC1, SC3, SC5 and SC12.
follows: FD1, FD2, FD3, FD4, FD5, FD8, FD9, FD10
---

A visitor or a patient chooses an appointment type, a doctor who gives it and one of that doctor's free times, and sees the price before going on to book.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The appointment types the staff defined, each with its length and price. | R6, R7, R13 |  |
| The doctors who give the type chosen, and their free times on the day chosen: the hours each sees patients, less those booked, one appointment starting as the one before it ends. | R14 |  |
| Names, times, prices and hours shown are samples, not the clinic's; the clinic's own come from the staff. | R13 |  |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C1 | region | The row every public screen starts with: the clinic's name, its pages, and the visitor's own links; each thing in it is a part of C1. | signed in: My bookings and Sign out in place of Sign in and Register | the banner | C1 |  | F1 |  |  |
| 2 | Book an appointment | heading | The page's title. |  | Book an appointment, heading level 1 |  | R6 |  | Q11, Q13 |  |
| 3 | Not for emergencies, C3 | message | Not for emergencies. A booked appointment is not emergency care. In a medical emergency, call 911. |  | note, the notice | C3 | R11 |  |  |  |
| 4 | No medical details | text | Please don't write symptoms or test results here: you talk about them with your doctor at the appointment. |  | the line |  | R6 |  | Q11, Q13 |  |
| 5 | Appointment type, C7 | field | Choose, then each type with its length and price, grouped by service; chosen already when opened from a type. |  | Appointment type, combo box | C7 | R6, R7 |  | Q11, Q13 |  |
| 6 | The price | text | Price: $120. The price of the type chosen, before anything is booked. | hidden until a type is chosen | Price, 120 dollars |  | R7 |  | Q13 |  |
| 7 | Doctor, C7 | field | Any doctor, then each doctor who gives the type chosen. |  | Doctor, combo box | C7 | R6, R14 |  | Q11, Q13 |  |
| 8 | Day, C7 | field | A day from today on. |  | Day, date | C7 | R6, R14 |  | Q11, Q13 |  |
| 9 | Free times | heading | The heading over the free times of the day chosen. |  | Free times, heading level 2 |  | R14 |  |  |  |
| 10 | A free time, C9 | button | A time the doctor is free; chosen, it is marked; the times repeat. | chosen | the time, toggle button | C9 | R14 |  |  |  |
| 11 | No free time that day, C8 | message | No doctor who gives First consultation is free on Friday, November 20. The nearest days with a free time: Monday, November 23 and Tuesday, November 24. | full | the message, announced when it appears | C8 | R6 |  | Q11, Q13 |  |
| 12 | Continue, C6 | button | Goes on to confirm the booking, or to sign in first. Leads to SC10, or SC9 signed out. |  | Continue | C6 | R6 |  | Q11, Q13 | SC9, SC10 |
| 13 | How we keep your details | link | The privacy notice, before anything is booked. Leads to SC7. |  | How we keep your details |  | R10 |  | Q11 | SC7 |
| 14 | Choose a time first, C8 | message | Choose a free time to continue. | validation | the message, announced when it appears | C8 | R6 |  | Q11, Q13 |  |
| 15 | The free times can't be shown, C8 | message | The free times can't be shown right now. Please try again, or call the clinic to book. | error | the message, announced when it appears | C8 | R6 |  | Q11, Q13 |  |
| 16 | Finding free times | text | Finding free times… | loading | Finding free times, busy |  | R14 |  |  |  |
| 17 | The site footer, C2 | region | The row every public screen ends with: the line on emergencies, Contact, Privacy and the staff's way in; each thing in it is a part of C2. |  | the footer | C2 | R11 |  |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Empty | added | no free times until a day is chosen. |  |  |
| Validation | added | Continue with no time chosen: "Choose a free time to continue.", element 14. |  |  |
| Error | added | The free times cannot be fetched: element 15, and the phone is in the footer's Contact. |  |  |
| Loading | added | While the free times of the day are fetched: "Finding free times…", element 16. |  |  |
| Success | n/a | Nothing is booked here: Continue leads on, to SC10, where the booking is made. |  |  |
| Disabled | n/a | Continue is always enabled; what is missing is said once it is chosen. |  |  |
| Unauthorized | n/a | Anyone may choose a time; signing in is asked when Continue is chosen (R6). |  |  |
| Full | stated | No doctor who gives the type is free on the day: element 11, with the nearest days that have a free time (R6). |  |  |
| Hover | added | A button and a free time darken under the pointer; a touch screen has nothing in its place; a button is at least 44 pixels high, a free time 40. |  |  |
| Keyboard | added | Tab reaches the header, then each field and button in reading order, then the footer; the focus shows as a clear outline; Enter on a button does what it says; a message that appears is announced. |  |  |
| Mobile | added | At 375 pixels every field takes the full width, each under its label, and the button stays below the last field. |  |  |
| Navigation | added | Back returns to the step before with what was chosen kept; a reload keeps what was chosen. |  |  |
| Permissions | stated | Anyone, signed in or not; only the patient's own name is ever booked (R6). |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | a type is chosen | normal |  | R6, R7 |  |
| normal | a day is chosen | loading |  | R14 |  |
| loading | the free times arrive | normal |  | R14 |  |
| loading | the free times cannot be fetched | error |  | R6 |  |
| normal | a day with no free time is chosen | full |  | R6 |  |
| normal | Continue, with no time chosen | validation |  | R6 |  |
| normal | Continue, signed out | SC9 | SC9 | R6 |  |
| normal | Continue, signed in | SC10 | SC10 | R6 |  |
| normal | How we keep your details is chosen | SC7 | SC7 | R10 |  |

## Variants

| What differs, and for whom | About |
|---|---|
| Signed in, the header offers My bookings and Sign out, and Continue leads straight to SC10. | C1, R6, SC10 |
| Opened from an appointment type's card, that type is chosen and its price shows. | R7 |

## Layout

| What | Must be | From |
|---|---|---|
| The notice on emergencies | above the form, before any field | R11 |
