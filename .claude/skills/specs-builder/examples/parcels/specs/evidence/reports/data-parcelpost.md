# Data archaeologist: what the Parcelpost API keeps

- **Role:** data
- **Read:** S2, models.py whole, and the key in auth.py
- **Version:** as it stands on 2026-10-11
- **Merged:** E48, E59 to E67

## Facets

| Facet | Found | Findings | Where looked |
|---|---|---|---|
| `entities` | found | E59, E65, E48: a shipment, a subscription, a key; an address, a parcel and a tracking event are a shipment's parts | the dataclasses of models.py and auth.py |
| `fields` | found | E62, E64, E65, E48 | the fields of each dataclass |
| `relations` | found | E30, E48: a shipment and a subscription belong to the account of the key that made them | the `account` fields |
| `constraints` | found | E63: the model's own comment on economy, which the code does not hold | models.py's comments; the limits are in app.py |
| `status-sets` | found | E59: eight statuses, created first; E62: three services; E64: four kinds of event | the enums of models.py |
| `lifecycle-columns` | found | E65: active and failures, which mark a paused subscription | the fields of Subscription |
| `tenancy` | found | E30, E48: every shipment and subscription is an account's | `account` on each |
| `audit` | found | E64: a shipment's events are its history, each with its time and place | TrackingEvent |
| `migrations` | none | | no migration: the demo keeps its things in memory |
| `seeds` | none | | the two keys of auth.py stand in for the accounts database, and are not reference values |
| `retention` | none | | nothing says how long a shipment or its events are kept |
| `identifiers` | found | E18, E67: PP and twelve digits for a shipment, WH and eight hexadecimal characters for a subscription | the ids made in app.py, the comments of models.py |

## Report

Read models.py whole and the key of auth.py.
Every set of states is named by a finding at its line: ShipmentStatus, E59; Service, E62; EventKind, E64.
Facets answered none: migrations, seeds, retention.
What the data could not tell: how long a shipment and its events are kept, and where the shipments are stored outside the demo's memory.
