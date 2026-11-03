---
id: SC3
name: Order a cake
kind: form
address: /order
who: anyone; no account is needed
reached by: Order a cake in the header; Order this cake on a card, which brings the cake with it
shows: R3, R4, R5
follows: FD11, FD12, FD13, FD14, FD15, FD16, FD17, FD18, FD19, FD20
---

A customer orders a cake for pick-up at the bakery.

## Data

| What it shows or changes | Shows | About |
|---|---|---|
| The cakes that can be ordered, and the two sizes with their prices. | R3 | B3 |
| The order: its cake, size, pick-up day, words, allergies, name and phone number. | R3 | N2 |

## Elements

| # | Element | Kind | What it shows and does | States | Heard as | Component | Shows | About | Asks | Leads to |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Site header, C1 | region | The row every screen starts with; each thing in it is a part of C1. |  | the header | C1 |  |  |  |  |
| 2 | The title | heading | Order a cake. |  | Order a cake |  | R3 |  |  |  |
| 3 | The line | text | Says what to do, and that the customer pays when they pick it up. |  | the line |  |  | R3 |  |  |
| 5 | Please check | message | Please check the 3 details below, by how many. | validation | an alert |  | R4 |  |  |  |
| 6 | Cake, C4 | field | A list of the cakes, and only the cakes. |  | Cake | C4 | R3 | B3, D4 |  |  |
| 7 | Pick-up day, C4 | field | The day it is collected. |  | Pick-up day | C4 | R3, R5 | B1, B2, D6 |  |  |
| 8 | Your name, C4 | field | Who the order is for. |  | Your name | C4 | R3 |  |  |  |
| 9 | Phone number, C4 | field | How the bakery reaches them. |  | Phone number | C4 | R3 |  |  |  |
| 10 | Any allergies, C4 | field | Any allergies; optional. |  | Any allergies, optional | C4 | R3 | D5 |  |  |
| 11 | Place order, C5 | button | Sends the order; while it is sent it says Placing your order. | sending, in loading | Place order | C5 | R3 |  |  | SC4 |
| 13 | We could not place your order | message | Says it was not placed, that nothing entered is lost, and the phone number. | error | an alert |  | R3 | D7 |  |  |
| 15 | The cake chosen | region | A picture of the cake chosen, its name and what it costs, or a word to choose one. |  | your cake |  | R3 |  |  |  |
| 16 | Site footer, C2 | region | The row every screen ends with; each thing in it is a part of C2. |  | the footer | C2 | R8 |  |  |  |
| 17 | Size, C4 | field | Small, which serves 8, or large, which serves 14, with its price. |  | Size | C4 | R3 | N2 |  |  |
| 18 | Words on the cake, C4 | field | Up to 30 characters; optional. |  | Words on the cake, optional | C4 | R3, R4 | N2 |  |  |

## States

| State | Status | What it shows | Evidence | Investigation |
|---|---|---|---|---|
| empty | stated | As it opens from the menu: nothing chosen, nothing entered. Its normal view. |  |  |
| validation | stated | Please check, above the form, and under each detail what to fix; what was entered stays. |  |  |
| error | stated | We could not place your order, above Place order, with the phone number; what was entered stays. |  |  |
| loading | stated | Place order says Placing your order and cannot be pressed again; the fields cannot be changed. |  |  |
| success | stated | It leads to SC4. |  |  |
| disabled | n/a | The form can always be sent. |  |  |
| unauthorized | n/a | Anyone may order, with no account. |  |  |
| hover | stated | A field's edge darkens and Place order deepens; a touch screen has nothing in its place. |  |  |
| keyboard | stated | Tab reaches the details in order, then Place order; Enter in a field sends the form; a refused form moves the focus to Please check. |  |  |
| mobile | stated | At 375 pixels the cake chosen stands above the form as a short row, and Place order fills the width. |  |  |
| navigation | stated | An address naming a cake opens the form with it chosen; a reload empties the form; back returns to where the customer was. |  |  |
| permissions | stated | Everyone sees the same. |  |  |

## Transitions

| From | Event | To | Leads to | Shows | Evidence |
|---|---|---|---|---|---|
| empty | Place order, with something wrong | validation |  | R4 |  |
| validation | Place order, with everything right | loading |  | R3 |  |
| loading | the order is recorded | SC4 | SC4 | R3 |  |
| loading | the order cannot be recorded | error |  | R3 |  |
| error | Place order | loading |  | R3 |  |
