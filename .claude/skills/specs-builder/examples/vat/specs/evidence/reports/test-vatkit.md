# Test archaeologist: vatkit's tests

- **Role:** test
- **Read:** S2, test_vatkit.py, all fourteen tests; none was run
- **Version:** 2.3.0
- **Merged:** E44 to E61, 18 findings

## Facets

| Facet | Found | Findings | Where looked |
|---|---|---|---|
| `asserted-behaviour` | found | E44, E47, E49, E52, E55, E56, E57, E58: each test, as a caller would see it | every `assert` |
| `asserted-rules` | found | E45: EL is GR; E50: half up; E55: once per rate | the asserts on figures |
| `boundaries` | found | E50: 0.05, whose VAT is 0.0095; E51: three gross prices | test_vat_on_a_net_price_to_the_cent, test_net_and_vat_make_the_gross_to_the_cent |
| `failures` | found | E46, E48, E53, E54, E59: the refusals each test expects | every `pytest.raises` |
| `roles` | none | | no fixture makes a user: vatkit has none |
| `journeys` | none | | no test walks more than one call |
| `mocked-systems` | none | | nothing is mocked: vatkit calls nothing |
| `fixtures` | none | | each test builds its own figures |
| `skipped` | found | E60: a rate changed during 2026, skipped until the rates follow on release | `pytest.mark.skip` |
| `untested` | found | E61: the command line, round_cents alone, a VAT number of a member state with no form | the tests set beside cli.py and numbers.py |
| `reports` | none | | no test report was given |
| `naming` | none | | no test names a requirement |

## Report

Read the one file of unit tests, all fourteen cases; none was run, as none was allowed.
The scan listed fifteen places, fourteen cases and one skip; each is named by a finding.
The tests pin the rules of the rates, half up, once per rate, no float and nothing below zero.
The test of the net lets the net and the VAT on it miss the gross by a cent, where the note on net says always: X1.
Facets answered none: roles, journeys, mocked-systems, fixtures, reports, naming.
What the tests could not tell: whether they pass today, and which rates of Finland and Romania changed during 2026, which the skipped test names and does not hold.
