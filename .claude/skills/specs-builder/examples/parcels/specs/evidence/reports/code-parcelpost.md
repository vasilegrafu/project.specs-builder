# Code archaeologist: the Parcelpost API's code

- **Role:** code
- **Read:** S2, the API's code, parcelpost/: app.py, auth.py and webhooks.py whole; models.py left to the data archaeologist, met where a route reaches it
- **Version:** as it stands on 2026-10-11
- **Merged:** E11 to E58, 48 findings

## Facets

| Facet | Found | Findings | Where looked |
|---|---|---|---|
| `routes` | found | E11, E19, E21, E23, E24, E28, E31, E35, E37: nine routes, each named by its line | the decorators of app.py |
| `controllers` | found | E16, E25, E26, E29, E32, E34: what each handler refuses, changes and answers | the handlers of app.py |
| `services` | found | E14, E38, E39: the girth worked out, and who is told of a change | app.py, the girth and notify |
| `components` | n/a | | no interface: the API has no pages, E92 |
| `messages` | found | E16, E25, E29, E32, E44, E45: each refusal's words | the `HTTPException` details of app.py and auth.py |
| `validation` | found | E12, E13, E14, E15, E17, E33: the limits of a parcel, the countries, economy's weight, https only | the constants and the `Field` limits of app.py |
| `states` | found | E26, E28, E61: what moves a shipment to labelled and to cancelled; the rest is the depot feed's | the assignments of `status` in app.py |
| `integrations` | found | E38, E39, E41, E57, E58: the webhook deliveries sent, signed and named; what sends a delivery attempted is not here | webhooks.py, notify in app.py |
| `feature-flags` | none | | app.py, auth.py, webhooks.py: no flag or toggle |
| `permissions` | found | E30, E36, E42, E43, E44, E45: a key, its scopes, its account | auth.py, `needs` in every route |
| `configuration` | found | E20, E40, E51: the page size, a rate limit nothing reads, the ten seconds a try | the constants of app.py and webhooks.py |
| `dependencies` | found | E47: the accounts database, which holds the keys | auth.py's comment; the framework is not a finding |
| `errors` | found | E49, E52, E54: what is tried again, when a subscription is paused, what is lost while it is | `deliver` in webhooks.py |
| `jobs` | found | E49: the queue's worker tries a failed delivery again after its wait | `schedule_retry` in webhooks.py |

## Report

Read app.py, auth.py and webhooks.py whole; __init__.py holds a line and nothing of the product.
The scan listed nine routes and three sets of states: every route is named by a finding at its line, and the sets of states are the data archaeologist's, E59, E62, E64.
Facets answered none: feature-flags; components does not apply to an API.
The three findings that matter most for the main journey: E11, a shipment registered within the limits; E25, no label for a cancelled shipment; E52, a subscription paused at its tenth failed try, every try counted.
What the code could not tell: whether the 600 calls a minute it declares are held anywhere, E40; what sends shipment.delivery.attempted, E41; how the depot feed moves a shipment from collected on, which is not in the material.
