# API archaeologist: the Parcelpost API's description

- **Role:** api
- **Read:** S3, the API's description, openapi.json, all nine endpoints and both webhooks, as the server writes it from its routes; set beside the routes of S2
- **Version:** 2026-10, as the server writes it
- **Merged:** E68 to E81, 14 findings

## Facets

| Facet | Found | Findings | Where looked |
|---|---|---|---|
| `endpoints` | found | E68, E70, E71, E72, E73, E74, E75, E76, E77: nine endpoints, each by its line | the description's paths |
| `parameters` | found | E70: status, reference and page; E71: a shipment's id, PP and twelve digits | `parameters` |
| `request-bodies` | found | E68, E69: a shipment; E75: a subscription | `requestBody` and the schemas ShipmentIn and SubscriptionIn |
| `responses` | found | E81: the eight statuses; E74: the label; E75: the secret, this once | `components.schemas` |
| `status-codes` | found | E69: 422 for a refused field; E71: 404 for another account's; E72: 409 once collected | `responses` |
| `errors` | none | | the description gives each status's words and no shape; the code gives the shape, E16 |
| `authentication` | found | E80: a bearer key | `securitySchemes` |
| `authorization` | found | E80: four scopes, one asked by each endpoint; E71: another account's shipment is 404 | `security` of each operation |
| `side-effects` | found | E68: a shipment made; E72: a shipment cancelled, its label void; E74: the shipment labelled; E75: a subscription made | the non-GET methods |
| `pagination` | found | E70: fifty to a page, from page 1 | the list's `page` |
| `versioning` | found | E68: v1 in the path, version 2026-10 | `info.version`, the paths |
| `events` | found | E78, E79: shipment.status.changed and shipment.delivery.attempted | `webhooks` |
| `traces` | n/a | | no trace or log of requests was given |
| `agreement` | found | X1: six hours against the code's tries; X3: no 403 for four endpoints whose routes refuse a key without the scope | the description beside the routes |

## Disagreements

- The description says a delivery is tried five times over six hours, E78; the code's waits add up to 8 hours and 36 minutes, E49.
- The description lists no 403 for one shipment, its events, the list of subscriptions and stopping one, E71, E73, E76, E77; each route asks for its scope, E36.

## Report

Read the description whole, endpoint by endpoint, with the line each stands at, and set each beside its route.
The brief says the server writes the description from its routes, so it is read as the API itself: seen.
Every endpoint became a finding and an endpoint page; the two webhooks became the event pages A10 and A11.
Endpoints that change data or send a message: registering, the label and cancelling, which tell the subscribers; subscribing and stopping.
Facets answered none: errors; traces does not apply.
What the description could not tell: what sends a delivery attempted, and what an integrator sees when a subscription is paused.
