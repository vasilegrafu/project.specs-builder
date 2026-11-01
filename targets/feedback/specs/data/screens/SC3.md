---
id: SC3
name: The request by email
kind: message
who: the customer it is sent to
reached by: sent when an order is delivered
shows: R13, R14, R15, R17
---

A customer who bought is asked for feedback by email.

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | From | text | The business's name. |  | From |  |  |  | Q17 |  |
| 2 | Subject | text | How was your order? |  | Subject |  | R13 |  |  |  |
| 3 | The words | text | Says the order has arrived, and asks for feedback. |  | the message |  | R13 |  | Q14 |  |
| 4 | Give feedback | link | Opens the feedback page. Leads to SC1. |  | Give feedback | C3 | R13 |  |  | SC1 |
| 5 | Stop these emails | link | Opens the page that stops requests. Leads to SC2. |  | Stop these emails |  | R17 |  | Q14 | SC2 |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| none | n/a | n/a: a message has no states of its own. |  |  |
| hover | n/a | n/a: it is read in the customer's or staff member's own email or message program. |  |  |
| keyboard | n/a | n/a: their own program decides that. |  |  |
| mobile | n/a | n/a: their own program decides that. |  |  |
| navigation | n/a | n/a: it has no address. |  |  |
| permissions | added | Only the customer it is sent to. |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Give feedback is selected | SC1 | SC1 | R13 |  |
| normal | Stop these emails is selected | SC2 | SC2 | R17 |  |
