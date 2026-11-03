# API archaeologist: the Voltline shop's API

- **Role:** api
- **Read:** S3, the shop's API description, openapi.json, all thirteen endpoints, as the server writes it from its routes; set beside the captures of S2
- **Version:** version 1, as served on 2026-10-11
- **Merged:** E57 to E74, 18 findings

## Facets

| Facet | Found | Findings | Where looked |
|---|---|---|---|
| `endpoints` | found | E57, E59, E60, E61, E62, E63, E64, E65, E67, E68, E69, E70: thirteen endpoints | the description's paths |
| `parameters` | found | E57: category, q, page and sort; E64: an order's number | `parameters` |
| `request-bodies` | found | E61: slug and qty; E63: address, payment and code; E69: name, email, password and terms | `requestBody` |
| `responses` | found | E73: a product's fields; E72: an order's statuses; E74: an address | `components.schemas` |
| `status-codes` | found | E59: 404 for no product; E60: 401 signed out; E61: 409 out of stock; E66: 403 for a customer | `responses` |
| `errors` | none | | the description: no shape of an error is given, only each status's words |
| `authentication` | found | E71: the session cookie | `securitySchemes` |
| `authorization` | found | E64: another customer's order is 404; E66: the admin's scope to move an order | `security`, the 403 and 404 rows |
| `side-effects` | found | E61: a line added; E63: an order made; E65: an order moved; E68: a session ended | the non-GET methods |
| `pagination` | found | E57, E58: page, from 1 | the products' `page` |
| `versioning` | found | E57: version 1, under /api/v1 | `servers`, `info.version` |
| `events` | none | | the description: no webhook and no callback |
| `traces` | n/a | | no trace or log of requests was given |
| `agreement` | found | X1: the description's "of four" pages against the walk's two | the description beside the captures |

## Report

Read the description whole, endpoint by endpoint, with the line each stands at, and set each beside what the captures show.
The owner says the server writes the description from its routes, so it is read as the shop itself: seen.
Every endpoint became a finding and an endpoint page; one remark disagrees with the walk, X1.
Facets answered none: errors, events; traces does not apply.
What the description could not tell: the words a refusal carries, which the pages show; how long a visitor's cart lives before they sign in.
