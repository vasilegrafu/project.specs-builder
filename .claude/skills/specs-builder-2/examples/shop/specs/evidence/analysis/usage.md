# The usage of the Voltline shop

- **Role:** usage
- **Read:** the findings E7 to E56; the captures V1 and V3 to V34 of S2 and their inventory; their screenshots at 1280 and 375 pixels

## Screens

| Screen | Kind | Views | What the user comes here to do | Findings |
|---|---|---|---|---|
| the home page | page | V1 | see what the shop has this week, and go into it | E7, E53 |
| a category | list | V3, V4 | look through a category's products, sort and filter them | E9, E10, E11, E12 |
| a product | detail | V5, V6, V7 | read one product, and put it in the cart | E13, E15, E16 |
| the search's results | list | V8, V9 | find the products that hold their words | E18, E19 |
| the cart | list | V10, V21 | change what they have chosen, and go to the checkout | E20, E21, E22 |
| the checkout | form | V22 | give the address and the way to pay, and place the order | E25 |
| sign in | form | V11, V12 | sign in | E26, E27 |
| create an account | form | V13, V14 | make an account | E28, E29 |
| the password | form | V15, V16 | get a link to choose a new password | E31, E32 |
| signed out | page | V32 | learn that the cart is kept, and go back | E33 |
| the profile | form | V23 | keep their details | E34 |
| my orders | list | V24 | see their orders | E35 |
| an order of mine | detail | V25, V34 | see where an order stands, and cancel it while it is placed | E36, E37 |
| the admin's orders | list | V26, V27, V28, V29 | see every order by status, and open one | E38, E55 |
| an order for the admin | detail | V30 | move an order on, and add a note | E39 |
| not allowed | page | V31 | learn that the admin's part is not theirs | E40 |
| about the shop | page | V17, V18, V19, V20 | read who the shop is, its terms and its delivery | E41, E51, E52 |
| page not found | page | V33 | learn that there is no page at the address | E43 |

## Not screens

| View | Why |
|---|---|
| V2 | the home page under its file name, not captured: it is V1 |

## Navigation

| From | How | To | Findings |
|---|---|---|---|
| any screen | the mark, a category, the search, Sign in, Sign up and the cart, in the header | the home page, a category, the search's results, sign in, create an account, the cart | E8 |
| the home page | a tile, a card, a popular search | a category, a product, the search's results | E7, E53 |
| a category | a card; a page's number | a product; the category at that page | E9, E12 |
| a product | Add to cart | the cart | E14 |
| the cart | Checkout | the checkout | E22 |
| any screen, signed in | the menu under the name | the profile, my orders, the admin's orders, signed out | E24 |
| my orders | an order's number | an order of mine | E35 |
| the admin's orders | a filter; an order's number | the same list, filtered; an order for the admin | E38, E55 |

## Components

| Component | Seen in | Variants and states seen | Findings |
|---|---|---|---|
| the site header | every view | signed out; signed in, with the menu | E8, E24 |
| the product card | V1, V3, V4, V8 | in stock; few left; out of stock, Add to cart disabled | E13, E56 |
| the price | every card, V5 | with a deal; without | E13 |
| the stock | every card, V5, V6, V7 | in, few left, out | E15, E16 |
| the primary button | every view | at rest; darker under the pointer; disabled | E44, E45 |
| the refusal above a form | V12, V14 | one | E27, E29, E47 |
| a field with its message | V12, V14 | at rest; refused, with its reason | E29 |
| the cart's line | V21 | at rest; minus and plus grey under the pointer | E21, E48 |
| the order's status | V24, V25, V26 | placed, paid, shipped, delivered, cancelled | E35, E38 |
| the pages | V3, V4 | the first page open; the last | E12 |

## Layouts

| Screen | Regions, and what is in each | At 768 | At 375 | Findings |
|---|---|---|---|---|
| a category | the header; the crumbs; the title; the count and the sort; the filters beside the grid; the pages | the filters hidden, three cards to a row | one card to a row | E9, E49 |
| a product | the header; the crumbs; the picture beside the facts; the specifications; the reviews; three more products | the same | the picture above the facts | E13 |
| the cart | the header; the lines beside the summary | the summary under the lines | each line a block | E21, E22 |

## Entry points

| Entry | Who comes in there | What they find | Findings |
|---|---|---|---|
| the shop's address | anyone | the home page | E7 |
| a product's address, from a search engine | anyone | the product | E13 |
| the admin's address | the admin; a customer who tries it | the admin's orders; the door | E38, E40 |

## Goals

| User | What they come to get done | Findings |
|---|---|---|
| the visitor | find a product and buy it | E2, E7 |
| the customer | follow their orders and keep their details | E35, E34 |
| the admin | move each order from placed to delivered | E39 |

## Flows

### Buy a product: from arriving to an order placed

- **User:** the visitor
- **Goal:** an order placed

| Step | Where | The user does | The product shows | Findings |
|---|---|---|---|---|
| 1 | the home page, a category, the search | browses or searches | the products, four to a page | E7, E9, E18 |
| 2 | a product | reads it, chooses a quantity, adds it | the cart | E13, E14 |
| 3 | the cart | changes a quantity, goes to the checkout | the checkout | E21, E22 |
| 4 | the checkout | gives the address and the way to pay, places the order | not seen: a stop point | E25 |

Branches:
- at step 1, if nothing matches: the search says so (E19)
- at step 2, if the product is out of stock: Add to cart is disabled (E15)

## Decisions

| Where | What the user decides | The options | Findings |
|---|---|---|---|
| the checkout | how to pay | Card, PayPal, Invoice | E25 |
| an order of mine | whether to cancel it, while it is placed | Cancel this order, or not | E37 |

## States

| Screen or flow step | State | Status | Evidence | Investigation |
|---|---|---|---|---|
| the cart | empty | observed | E20 | |
| the search's results | no-results | observed | E19 | |
| a product | few-left | observed | E16 | |
| a product | out-of-stock | observed | E15 | |
| sign in | validation | observed | E27 | |
| create an account | validation | observed | E29 | |
| the password | success | observed | E32 | |
| an order of mine | placed | observed | E37 | |
| the checkout | success | likely | | place an order on a copy of the shop |

## Permissions

| Who | May | May not, and what they then see | Findings |
|---|---|---|---|
| a visitor | browse, search, fill a cart | the checkout and the account: sign in first | E20 |
| a customer | buy, see their orders, cancel one while placed | the admin's part: the door | E40 |
| the admin | see and move every order | | E50 |
