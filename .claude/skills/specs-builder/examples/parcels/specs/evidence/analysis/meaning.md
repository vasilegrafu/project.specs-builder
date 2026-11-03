# The meaning of the Parcelpost API

- **Role:** meaning
- **Read:** the findings E1 to E94 and the contradictions X1, X2 and X3

## Terms

| Term | Means | Also called | Findings |
|---|---|---|---|
| shipment | one parcel registered to be sent | parcel | E11, E59 |
| label | the A6 PDF the courier scans | | E24 |
| collected | the courier has the parcel | collection | E61, E72 |
| tracking event | one line of a shipment's history | event | E64 |
| webhook event | what a subscriber is told of | event, webhook | E55 |
| subscription | an address told of events | webhook | E31, E65 |
| delivery | one webhook event sent, and its tries | | E38, E51 |
| scope | what a key may do | | E42 |

## Entities

| Entity | What it is to a user | Fields | Findings |
|---|---|---|---|
| shipment | the parcel they send, and where it stands | id, status, service, sender, recipient, parcel, reference, events, label | E11, E18, E59 |
| webhook subscription | where they are told of moves | id, url, events, secret, active, failures | E31, E65 |
| API key | what their program calls with | account, scopes, test | E42, E48 |

## Lifecycles

| Entity | From | Event | To | Findings |
|---|---|---|---|---|
| shipment | created | the label is produced | labelled | E26 |
| shipment | created or labelled | the sender cancels | cancelled | E61 |
| shipment | labelled | the courier collects it | collected | E92 |
| shipment | collected, in transit, out for delivery | the depot feed moves it | the next | E59 |
| shipment | out for delivery | the third attempt fails, or a refusal | returned | E66 |
| subscription | active | the tenth failed try in a row | paused | E52 |
| subscription | active or paused | the integrator stops it | stopped | E37 |

## Rules

| Rule | Except | Findings |
|---|---|---|
| a parcel weighs up to 30 kg, each side up to 120 cm, a girth up to 300 cm | | E12, E13, E14 |
| a recipient in one of nine countries | | E15 |
| economy up to 20 kg | | E17, E69, E87 |
| a call needs its scope | | E36, E42, E45 |
| a failed delivery is tried five times more, then dropped | a paused subscription | E49 |
| ten failed tries in a row pause a subscription | | E52 |
| cancelled only before collection, and then no label | | E25, E61 |
| a key reaches its own account alone | | E30 |
| the secret is shown once | | E34 |

## Roles

| Role | Who | Findings |
|---|---|---|
| integrator | a key with every scope | E6, E43 |
| shop's site | a key that may only read | E6, E43, E84 |
| depot feed | the courier's depots, outside the API | E6, E92 |

## Unknowns

- Whether the limit of 600 calls a minute is held anywhere: no finding shows it held (E40).
- What sends a delivery attempted: no finding shows it sent (E41).
