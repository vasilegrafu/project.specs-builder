# Documentation archaeologist: the brief and the README

- **Role:** documentation
- **Read:** S1, the product owner's brief, whole; S5, the README, whole
- **Version:** the brief of 2026-10-11; the README as it stands on 2026-10-11
- **Merged:** E1 to E10, E92 to E94

## Facets

| Facet | Found | Findings | Where looked |
|---|---|---|---|
| `glossary` | none | | neither defines a term |
| `concepts` | found | E92: a shipment, its label, its tracking, the depots' scans | the README's first paragraph |
| `users-and-roles` | found | E6: the integrator, the shop's site, the depot feed | the brief's Who uses it |
| `workflows` | found | E92: register, label, follow, cancel, hear by webhook | the README's first paragraph |
| `stated-requirements` | found | E7: an email when a subscription is paused, wanted | the brief |
| `rules-and-numbers` | found | E10: nothing over 30 kg; E93: a test key's shipments never collected | the brief, the README |
| `wording` | none | | neither prescribes a word the API answers |
| `constraints` | found | E1: the rebuild on the courier's new platform in the first half of 2027 | the brief's first paragraph |
| `decisions` | found | E8: resuming a paused subscription is not for now; E9, E94: the description is the server's | the brief, the README |
| `needs-and-pains` | found | E2, E3, E4: missed webhooks, labels for cancelled shipments, the slow first label | the brief's What goes wrong today |
| `measures` | found | E2: 23 of 140 tickets; E3: 9 labels; E4: 6 working days | the brief |
| `dates-and-versions` | found | E1: the brief of 2026-10-11 | the brief's head |
| `records` | none | | no log or export was given; the tickets and the onboarding log are counted in the brief, not given |

## Report

Read the brief and the README whole.
The brief gives the problem, the goals and their numbers, the users, one wish and what is not for now; the README says what the API is and what it is not.
Facets answered none: glossary, wording, records.
What the documents could not tell: whether the tickets are counted the same way after the rebuild, which the document keeps as an assumption.
