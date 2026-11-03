---
id: SC5
name: Staff orders
kind: list
address: /staff/orders
who: staff who are signed in
reached by: Staff in the footer
shows: R9, R10, R11
displays: N2.placed, N2.ready
follows: FD11, FD12, FD13, FD14, FD15, FD16, FD17, FD18, FD19, FD20
---

The staff see the orders, the soonest pick-up day first, and mark each one ready.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The orders: each with its number, pick-up day, cake, size, words, allergies, name, phone number and status. | R9 | N2 |
| An order's status, changed by Mark ready. | R10 | N2 |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Site header, C1 | region | The row every screen starts with; each thing in it is a part of C1. |  | the header | C1 |  |  |  |  |
| 2 | The title | heading | Orders. |  | Orders |  | R9 |  |  |  |
| 5 | To do | heading | The heading over the orders not yet ready. |  | To do |  | R9 | N2.placed |  |  |
| 6 | Ready | heading | The heading over the orders marked ready. |  | Ready |  | R9 | N2.ready |  |  |
| 7 | An order, C6 | region | One order; each thing in it is a part of C6. The rest repeat, the soonest pick-up day first. |  | the order | C6 | R9, R10 |  |  |  |
| 8 | No orders yet | message | No orders yet, and that new ones show here. | empty | a status |  | R9 |  |  |  |
| 9 | We could not load the orders | message | Says the orders did not load, and to reload the page. | error | an alert |  | R9 |  |  |  |
| 13 | The sign-in's heading | heading | Staff sign in. | unauthorized, wrong-password | Staff sign in |  | R11 |  |  |  |
| 14 | Staff password, C4 | field | The password the staff share. | unauthorized, wrong-password | Staff password | C4 | R11 |  |  |  |
| 15 | Sign in, C5 | button | Sends the password. | unauthorized, wrong-password | Sign in | C5 | R11 |  |  |  |
| 16 | That password is not right | message | That password is not right. | wrong-password | an alert |  | R11 |  |  |  |
| 17 | Site footer, C2 | region | The row every screen ends with; each thing in it is a part of C2. |  | the footer | C2 |  |  |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| empty | stated | No orders yet, and that new ones show here. |  |  |
| loading | n/a | The orders come with the page, so nothing waits. |  |  |
| error | stated | We could not load the orders, and to reload the page. |  |  |
| no-results | n/a | The list is not searched or filtered. |  |  |
| unauthorized | stated | Staff sign in, with the password asked for; no order shows. |  |  |
| wrong-password | stated | Staff sign in again, saying That password is not right. |  |  |
| save-failed | stated | The order stays under To do and says That did not save. Try again. |  |  |
| hover | stated | Mark ready deepens; a touch screen has nothing in its place. |  |  |
| keyboard | stated | Tab reaches each order's phone number and Mark ready in turn; the focus always shows, and moves to the next order after a mark. |  |  |
| mobile | stated | At 375 pixels each order is a card: the day and status on top, Mark ready filling the width at its foot. |  |  |
| navigation | stated | The address opens the orders if signed in, else the password is asked for; a reload keeps the sign-in until the browser is closed. |  |  |
| permissions | stated | Staff see the orders; anyone else sees only Staff sign in. |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| unauthorized | Sign in, with the right password | normal |  | R11 |  |
| unauthorized | Sign in, with a wrong password | wrong-password |  | R11 |  |
| normal | Mark ready | normal |  | R10 |  |
| normal | Mark ready, and it cannot be saved | save-failed |  | R10 |  |
