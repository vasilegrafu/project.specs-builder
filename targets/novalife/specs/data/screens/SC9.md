---
id: SC9
name: Sign in
kind: form
address: /sign-in; /reset opens it to reset the password
who: anyone signed out; signed in, it leads to SC12
reached by: Sign in in the header, C1; Continue on SC8, signed out; Already have an account? on SC21
follows: FD1, FD2, FD3, FD4, FD5, FD8, FD9, FD10
---

A patient signs in, or asks for a link to set a new password; reached from booking, the time chosen is kept. Someone new goes on to create an account, SC21.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| To sign in: the email and the password. | R16 |  |
| To reset: the email, to which a link is sent. | R16 |  |
| From booking: the type, the doctor and the time chosen, kept. | R6 |  |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C1 | region | The row every public screen starts with: the clinic's name, its pages, and the visitor's own links; each thing in it is a part of C1. | signed in: My bookings and Sign out in place of Sign in and Register | the banner | C1 |  | F1 |  |  |
| 2 | Your NovaLife account | heading | The page's title. |  | Your NovaLife account, heading level 1 |  | R16 |  |  |  |
| 3 | The time kept | text | Sign in or create an account to book First consultation with Dr. Lee, Friday, November 20, 2026, 10:00 AM. We'll keep this time while you do. | only when reached from booking | the line |  | R6 |  | Q11, Q13 |  |
| 4 | Sign in | heading | The heading over signing in. | sign in | Sign in, heading level 2 |  | R16 |  |  |  |
| 5 | Email, C7 | field | The patient's email. |  | Email | C7 | R16 |  |  |  |
| 6 | Password, C7 | field | The patient's password. |  | Password | C7 | R16 |  |  |  |
| 7 | Sign in, the button, C6 | button | Signs in, then books on (SC10) or opens My bookings (SC12). |  | Sign in | C6 | R16 |  |  | SC10 |
| 8 | Forgot your password? | link | Opens the reset. Leads to SC9. |  | Forgot your password? |  | R16 |  |  | SC9 |
| 9 | Create an account | link | New to NovaLife? Create an account: the form of its own, with the time kept. Leads to SC21. |  | Create an account |  | R16 |  |  | SC21 |
| 10 | Sign-in refused, C8 | message | That email and password don't match an account. Try again, or reset your password. | validation | the message, announced when it appears | C8 | R16 |  |  |  |
| 18 | Reset your password | heading | The heading over the reset. | reset | Reset your password, heading level 2 |  | R16 |  |  |  |
| 19 | Email, to reset, C7 | field | The email the link goes to. |  | Email | C7 | R16 |  |  |  |
| 20 | Send the link, C6 | button | Sends a link that sets a new password. |  | Send the link | C6 | R16 |  |  |  |
| 21 | Link sent, C8 | message | If that email has an account, we've sent it a link to set a new password. | success | the message, announced when it appears | C8 | R16 |  |  |  |
| 22 | Can't sign in now, C8 | message | Signing in can't be done right now. Please try again in a moment. | error | the message, announced when it appears | C8 | R16 |  |  |  |
| 23 | The site footer, C2 | region | The row every public screen ends with: the line on emergencies, Contact, Privacy and the staff's way in; each thing in it is a part of C2. |  | the footer | C2 | R11 |  |  |  |
| 24 | New to NovaLife? | heading | The heading over the way to create an account. |  | New to NovaLife?, heading level 2 |  | R16 |  |  |  |
| 25 | Why an account | text | An account lets you book, see your bookings and cancel one, in one place. |  | the paragraph |  | R16, R17 |  |  |  |
| 26 | Back to sign in | link | From the reset, back to signing in. Leads to SC9. | reset | Back to sign in |  | R16 |  |  | SC9 |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Empty | stated | The fields blank, and, from booking, the time kept, element 3 (R6, R16). |  |  |
| Validation | stated | Sign-in refused with one message that does not say which was wrong, element 10 (R16). |  |  |
| Error | added | Signing in cannot be done: element 22. |  |  |
| Loading | added | While signing in, the button says Signing in… and cannot be pressed twice. |  |  |
| Success | stated | Signed in: on to SC10 from booking, or to SC12; to reset, the link sent, element 21 (R16). |  |  |
| Disabled | n/a | The buttons are always enabled; what is missing is said once one is chosen. |  |  |
| Unauthorized | n/a | Anyone signed out may sign in. |  |  |
| Hover | added | A button darkens under the pointer; a touch screen has nothing in its place, and a button is at least 44 pixels high. |  |  |
| Keyboard | added | Tab reaches the header, then each field and button in reading order, then the footer; the focus shows as a clear outline; Enter on a button does what it says; a message that appears is announced. |  |  |
| Mobile | added | At 375 pixels every field takes the full width, each under its label, and the button stays below the last field. |  |  |
| Navigation | added | Back returns to the step before with what was chosen kept; a reload keeps what was chosen. |  |  |
| Permissions | stated | Anyone signed out; a patient already signed in is taken to SC12. |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Sign in, with a wrong password or an unknown email | validation |  | R16 |  |
| normal | Sign in, right, from booking | SC10 | SC10 | R6 |  |
| normal | Sign in, right, not from booking | SC12 | SC12 | R16 |  |
| normal | Create an account is chosen | SC21 | SC21 | R16 |  |
| normal | Send the link | success |  | R16 |  |

## Variants

| What differs, and for whom | About |
|---|---|
| ?as=reset opens it to reset the password. | R16 |
| Reached from booking, it says which time is kept, element 3, and goes on to SC10. | R6, SC10 |
