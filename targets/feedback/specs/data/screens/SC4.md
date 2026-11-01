---
id: SC4
name: The request by text message
kind: message
who: the customer it is sent to
reached by: sent when an order is delivered, to a customer with no email address
shows: R13, R15, R17
---

A customer who bought is asked for feedback by text message.

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The words | text | The business's name, the question and the link to the feedback page. |  | the message |  | R15 |  | Q14 | SC1 |
| 2 | Stop these texts | link | Opens the page that stops requests. Leads to SC2. |  | Stop these texts |  | R17 |  | Q14 | SC2 |

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
| normal | The link in the message is selected | SC1 | SC1 | R13 |  |
| normal | Stop these texts is selected | SC2 | SC2 | R17 |  |
