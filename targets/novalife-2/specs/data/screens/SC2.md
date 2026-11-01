---
id: SC2
name: A service
kind: detail
address: /services/{service}: general-medical-care, prevention-and-early-detection, longevity-and-healthy-aging, high-tech-personalized-healthcare
who: anyone, signed in or not
reached by: a service on SC1; Services in the header, C1; a link on SC5
---

A visitor reads what one of NovaLife's four services covers, who it is for, and what its appointment types cost, and books one.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The service: its name and what it covers, as R2 names it, a line that opens it and who it is for, in the clinic's words. | R2 |  |
| Its appointment types, each with its length and its price in US dollars, set by the staff. | R7, R13 |  |
| Names, times, prices and hours shown are samples, not the clinic's; the clinic's own come from the staff. | R13 |  |
| Wording beyond what the brand and the requirements fix is a draft, proposed on 2026-10-20 for the clinic to replace through the staff area (R13); what it may say of health and longevity waits on Q12. | R13 | Q12 |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The site header, C1 | region | The row every public screen starts with: the clinic's name, its pages, and the visitor's own links; each thing in it is a part of C1. | signed in: My bookings and Sign out in place of Sign in and Register | the banner | C1 |  | F1 |  |  |
| 2 | The service's name | heading | The service: General medical care, or one of the other three. |  | the service, heading level 2 |  | R2 |  | Q12 |  |
| 3 | What it covers | heading | The heading over what the service covers. |  | What it covers, heading level 3 |  | R2 |  | Q12 |  |
| 4 | One thing it covers | text | An item of the list, as R2 names it; the items repeat. |  | the item, of a list |  | R2 |  | Q12 |  |
| 5 | Who it is for | heading | The heading over who the service is for. |  | Who it is for, heading level 3 |  | R2 |  | Q12 |  |
| 6 | Who it is for, said | text | Who the service is for, in a draft of the clinic's words. |  | the paragraph |  | R2 |  | Q12 |  |
| 7 | Technology supports | text | "Technology supports the clinicians and does not replace their judgment." | high-tech only | the line |  | R2 |  | Q12 |  |
| 8 | The limit of the ambition | text | "Immortality is an aspirational idea, not a current medical capability or a promise NovaLife Clinic makes." | longevity only | the line |  | R4 |  | Q12 |  |
| 9 | Appointment types and prices | heading | The heading over the service's appointment types. |  | Appointment types and prices, heading level 3 |  | R7 |  | Q13 |  |
| 10 | An appointment type, C4 | region | One appointment type of the service, with its length and price; the cards repeat. Its parts are C4's; Book this opens booking with the type chosen. |  | the type's name, its length and price | C4 | R7 |  | Q13 |  |
| 11 | Who pays | text | "Patients pay NovaLife Clinic themselves. The clinic does not bill health insurance." |  | the line |  | R7 |  | Q13 |  |
| 12 | No such service, C8 | message | "We couldn't find that service." and the four by name. | not-found | the message | C8 | R2 |  | Q12 |  |
| 13 | The page can't be shown, C8 | message | "This page can't be shown right now. Please try again in a moment, or call the clinic." | error | the message, announced when it appears | C8 |  |  |  |  |
| 14 | The site footer, C2 | region | The row every public screen ends with: the line on emergencies, Contact, Privacy and the staff's way in; each thing in it is a part of C2. |  | the footer | C2 | R11 |  |  |  |
| 15 | Services | heading | The page's title, over the service shown. |  | Services, heading level 1 |  | R2 |  | Q12 |  |
| 16 | The service's opening line | text | A sentence on what the service is for, in a draft of the clinic's words. |  | the paragraph |  | R2 |  | Q12 |  |
| 17 | How to become a patient | link | New to NovaLife? How to become a patient. Leads to SC5. |  | How to become a patient |  | R9 |  |  | SC5 |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| Loading | n/a | It opens with its words and its types; nothing is fetched after it opens. |  |  |
| Error | added | The header, the footer and, in place of the service, "This page can't be shown right now. Please try again in a moment, or call the clinic.", element 13. |  |  |
| Not-found | added | An address of no service: "We couldn't find that service.", and the four by name, element 12. |  |  |
| Unauthorized | n/a | Anyone may read a service's page. |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Book this is chosen on an appointment type | SC8 | SC8 | R6 |  |
| normal | How to become a patient is chosen | SC5 | SC5 | R9 |  |
| normal | an address of no service is opened | not-found |  | R2 |  |
| not-found | a service is chosen in the header | SC2 | SC2 | R2 |  |

## Variants

| What differs, and for whom | About |
|---|---|
| One of four, by its address: General medical care is drawn first; ?as=prevention, ?as=longevity and ?as=high-tech show the others, each with what R2 names for it. | R2 |
| Longevity and healthy aging adds the limit of the ambition, element 8. | R4 |
| High-tech, personalized healthcare adds that technology supports the clinicians, element 7. | R2 |
