# Test archaeologist: what the Parcelpost API's tests promise

- **Role:** test
- **Read:** S4, tests/test_shipments.py whole: ten tests through the API's own client, one skipped
- **Version:** as it stands on 2026-10-11
- **Merged:** E82 to E91, 10 findings

## Facets

| Facet | Found | Findings | Where looked |
|---|---|---|---|
| `asserted-behaviour` | found | E82, E88, E89: a shipment made, a label the same twice, a cancelled shipment with no label | the asserts of each test |
| `asserted-rules` | found | E85, E86, E87: a country not served, 31 kg, economy at 25 kg | the asserts on 422 |
| `boundaries` | found | E86, E87: 31 kg, one past the limit; economy at 25 kg, not at 20 or 21 | the values the tests send |
| `failures` | found | E83, E84, E89, E90: 401, 403 naming the scope, 409, 404 | the asserts on status codes |
| `roles` | found | E84: a key with every scope, and a key that may only read | the fixtures KEY and TRACK_ONLY |
| `journeys` | none | | no test walks from a shipment to its delivery |
| `mocked-systems` | none | | nothing is mocked; the depot feed is left out, E91 |
| `fixtures` | found | E82: one address and one parcel of 1.2 kg, 40 by 30 by 10 cm, a reference of an order | ADDRESS, PARCEL and the helper `shipment` |
| `skipped` | found | E91: a scan that leaves the status as it was, skipped for want of the depot feed | `pytest.mark.skip` |
| `untested` | found | E90: another account's shipment is not tried; nothing subscribes, delivers, retries or pauses; no list of shipments | the routes of app.py beside the tests |
| `reports` | none | | no report of a run was given |
| `naming` | none | | no test names a requirement |

## Report

Read the one file of tests, ten cases, one of them skipped; all ten are named by a finding at their line.
The tests pin down the limits of a parcel, the countries, economy's weight, the key and its scopes, the label and the cancelling.
Nothing is mocked; the skipped test is a decision, for the depot feed is not in the tests, E91.
Untested: every webhook route and the deliveries, the list of shipments, another account's shipment, though a test's name says so, E90.
What the tests could not tell: whether they pass today, since none was run.
