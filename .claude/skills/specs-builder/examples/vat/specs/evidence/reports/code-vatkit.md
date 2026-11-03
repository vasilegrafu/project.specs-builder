# Code archaeologist: vatkit's code

- **Role:** code
- **Read:** S1, vatkit's seven modules, all of them, by their syntax with Python's own parser; the tests left to the test archaeologist
- **Version:** 2.3.0, as `__version__` says
- **Merged:** E1 to E43, 43 findings

## Facets

| Facet | Found | Findings | Where looked |
|---|---|---|---|
| `routes` | found | E37, E38, E39: the commands vat, gross, net, rate and check; E1: the eight public functions | cli.py, `__all__` in __init__.py |
| `controllers` | found | E40, E41, E42, E43: what each command prints, and what it does with a refusal | `main` in cli.py |
| `services` | found | E12, E13, E14, E16, E17, E18, E19: the VAT, the gross, the net and a sale split by rate | compute.py |
| `components` | none | | no interface but the command line's lines of text |
| `messages` | found | E7, E11, E20, E21, E22, E29, E30: every refusal's words; E42: "vatkit:" before each at the shell | each `raise`, and cli.py |
| `validation` | found | E10, E20, E21, E22, E28, E29, E30, E32, E33: what is refused, at what value | money.py, numbers.py, rates.py |
| `states` | none | | no enum and no status: the scan listed no set of states |
| `integrations` | none | E34, E35: VIES is named and never called | every import |
| `feature-flags` | none | | no setting is read anywhere |
| `permissions` | none | | nothing checks who calls |
| `configuration` | found | E2: the day the rates hold; E4, E5, E6: the rates; E24, E25, E26: how each country writes an amount; E31: the forms of VAT numbers | the constants of rates.py, money.py and numbers.py |
| `dependencies` | none | E35: Python's own modules only | every import |
| `errors` | found | E36: each refusal a ValueError; E42: the command line ends with 2 | errors.py, cli.py |
| `jobs` | none | | nothing runs by itself |

## Report

Read all seven modules, each from top to bottom, and set every refusal the scan listed beside the function it ends.
The scan listed no route and no set of states; the five commands and the eight functions are each named by a finding.
Facets answered none: components, states, integrations, feature-flags, permissions, dependencies, jobs.
The three that matter most for the invoice: E17, the VAT once per rate; E23, half up to the cent; E7, no standard rate behind the caller's back.
Two notes in the code disagree with the code or its tests, X1 and X2.
What the code could not tell: why a release follows a change of a rate within a month and not on its day, and which of the 17 member states with no form for their VAT numbers the invoicing meets.
