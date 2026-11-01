---
id: SC1
name: Home
kind: page
address: /
who: anyone
reached by: the mark in the header, on every screen; Find us in the header
shows: R1, R8
---

A customer sees what the bakery is about, what it bakes, and when it is open and where it is.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The three cakes. | R1 | N1 |
| The bakery's hours, address and phone number. | R8 | N3 |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Site header, C1 | region | The row every screen starts with; each thing in it is a part of C1. |  | the header | C1 |  |  |  |  |
| 2 | The welcome | heading | What the website is for, in a line. |  | the title, as it reads |  |  |  |  |  |
| 3 | The welcome's line | text | Says what can be done here. |  | the line |  |  |  |  |  |
| 4 | Order a cake, C5 | link | The main button; leads to SC3. |  | Order a cake | C5 | R3 |  |  | SC3 |
| 5 | See what we bake, C5 | link | The quiet button; leads to SC2. |  | See what we bake | C5 | R1 |  |  | SC2 |
| 6 | A picture of a cake | image | A picture of a cake. |  | a picture of a cake |  |  |  |  |  |
| 7 | From our oven | heading | The heading over the three cakes. |  | From our oven |  | R1 |  |  |  |
| 8 | A product card, C3 | region | The three cakes; each thing in it is a part of C3. |  | the product | C3 | R1 |  |  |  |
| 10 | Find us | heading | The heading over the hours and the address. |  | Find us |  | R8 |  |  |  |
| 13 | A day and its hours | text | One of the seven days with its hours, or Closed. The rest repeat. |  | the day and its hours |  | R8 | N3, D7 |  |  |
| 15 | The address | text | Where the bakery is. |  | the address |  | R8 | N3, D7 |  |  |
| 16 | The phone number | link | The bakery's number; a phone offers to ring it. |  | the phone number |  | R8 | N3, D7 |  |  |
| 17 | A picture of the shop | image | A picture of the bakery. |  | a picture of the bakery |  |  |  |  |  |
| 18 | Site footer, C2 | region | The row every screen ends with; each thing in it is a part of C2. |  | the footer | C2 | R8 |  |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| empty | n/a | All it shows comes with the page. |  |  |
| loading | n/a | Nothing on it waits. |  |  |
| error | n/a | It asks nothing of a server once it is open. |  |  |
| hover | stated | A button deepens and a card lifts; a touch screen has nothing in its place. |  |  |
| keyboard | stated | Tab reaches Skip to content, the header, the two buttons, each Order this cake, the phone number, then the footer; the focus always shows. |  |  |
| mobile | stated | At 375 pixels the picture moves under the welcome, the cards stand one above another and Find us folds to one column. |  |  |
| navigation | stated | The address opens it as it is; Find us leads to its heading. |  |  |
| permissions | stated | Everyone sees the same. |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| normal | Find us, in the header | normal |  | R8 |  |
| normal | Order a cake | SC3 | SC3 | R3 |  |
| normal | See what we bake | SC2 | SC2 | R1 |  |
| normal | Order this cake, on a card | SC3 | SC3 | R3 |  |
