# The examples: seven products, and the specification of each

One folder per kind of product the skill writes for. In each, `dev/` is
the material -- a site to walk, code to read, a description, a log, a
runbook -- and `specs/` is the specification read from it: its data, its
prototypes, its evidence with what was read, and the application that
opens it. Each was written by specs-builder and brought over whole by
`scripts/import_site.py`, its captures, reports and analyses with it.
Every product, person, number and address in them is made up. The bakery has no
`dev/`: it was written from a conversation, and the tutorial follows how.

| Case | Kind | The product | The material, `dev/` | How it was read |
|---|---|---|---|---|
| bakery | application | Mill Lane Bakery, the smallest site with a design system and a prototype | none: the owner's words and answers | written in a session with Claude Code, the tutorial's example |
| shop | application, api | Voltline, a small electronics shop | 84 static pages of HTML and CSS, every state a page of its own, and the API's description | walked view by view; the description read endpoint by endpoint |
| clinic | application | Larkfield Clinic, a family practice's site | 28 static pages: the doctors, booking a visit and its refusals, my visits, cancelling one | walked, its forms filled and refused by hand, nothing sent |
| parcels | api | Parcelpost, an API a shop calls to send parcels | a FastAPI service in Python, its description, its tests | its routes and its description, by line |
| cart | part, api | the cart of the shop's back end | the back end in Python, a package per part; the cart is the part | the cart in full; the parts around it for what crosses its edge |
| stock-sync | process, library | a nightly job that brings the shop's stock in line with its supplier | the job in Python, its schedule, its configuration, a night's log, the runbook, its tests | the code, the log and the runbook |
| vat | library | vatkit, the VAT of a sale in the EU | a small Python library, its command line, its tests, the README and the changelog | the code and the documents |

The shop is the fullest: the scout's report, two agents' reports and two
analyses, a site's captures with their screenshots, the Domain, flows,
screens with their prototypes, a design system and endpoints. The
selftest breaks copies of its specification, one fault to a check, to
prove that each check fires.

## To open a specification

Run its launcher, `specs/index.cmd` (or `specs/index.sh`), which starts
its application and opens the browser on it; or ask its command line,
`python specs/app/spec.py overview`, `open`, `trace R4`.

## To walk or run the material

The shop and the clinic are static sites: serve `dev/` and walk it at the
address the server gives, `python -m http.server 8080 --bind 127.0.0.1`
in `dev/`. The rest is code and documents, read where they stand.
