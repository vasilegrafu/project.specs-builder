# Documentation archaeologist: vatkit's README, its changelog and the brief

- **Role:** documentation
- **Read:** S3, the README; S4, the changelog from 1.4.0 to 2.3.0; S5, the finance lead's brief; all of each
- **Version:** 2.3.0 for the README and the changelog; the brief of 2026-10-11
- **Merged:** E62 to E86, 25 findings

## Facets

| Facet | Found | Findings | Where looked |
|---|---|---|---|
| `glossary` | found | E68: VIES | the README |
| `concepts` | found | E66: a sale and its lines; E77: a category | the README's promises, the changelog |
| `users-and-roles` | found | E62, E82: the programs that call it, the three at the shell, the maintainer | the README, the brief |
| `workflows` | found | E86: the README's example of the calls an invoice makes; E69, E71, E83: a release after each change of a rate | the README's Versions, the changelog, the brief |
| `stated-requirements` | found | E64, E65, E66, E67, E68: the README's five promises; E81: each change on the day it is in force | the README's What it promises, the brief |
| `rules-and-numbers` | found | E69: within a month; E70: the major version; E73, E77: EL, the reduced rates | the README, the changelog |
| `wording` | found | E72: a rate named as an invoice writes it | the changelog |
| `constraints` | found | E70: the major version changes only with a function's name or what it takes | the README's Versions |
| `decisions` | found | E75, E76: no float, and once per rate, both from 2.0.0 | the changelog |
| `needs-and-pains` | found | E79, E80: invoices a few cents off, and a change of a rate eleven days late | the brief |
| `measures` | found | E79: 37 of 4,100 in 2024, none of 3,900 in 2025; E80: 214 invoices | the brief |
| `dates-and-versions` | found | E71: 2.3.0 on 2026-01-12, Finland's rate from 1 January 2026 | the changelog's headings |
| `records` | none | | no log or count of the product running was given |

## Report

Read the README, the changelog and the brief, each whole.
The README's promises are what the code does, each corroborated by a finding of the code or the tests.
The README and the note on the rates promise a release within a month of a change; the brief wants it on the day, which the user chose, under Decisions.
The changelog and the code agree that France writes its thousands with a narrow space.
Facets answered none: records.
What the text could not tell: whether the back office's checks at the shell find anything the invoicing does not, and how a release reaches the invoicing.
