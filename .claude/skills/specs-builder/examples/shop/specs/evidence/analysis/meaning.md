# The meaning of the Voltline shop

- **Role:** meaning
- **Read:** the findings E1 to E74 and the contradiction X1; the usage analysis

## Terms

| Term | Means | Also called | Findings |
|---|---|---|---|
| product | one thing the shop sells | item, on the cart and the order | E13, E73 |
| deal | a product under its old price, while its stock at that price lasts | | E13, E42 |
| cart | what is chosen and not yet ordered | | E21, E60 |
| order | a cart placed, with its address and its status | | E36, E72 |
| open order | placed or paid, not yet shipped | | E38, E55 |
| admin | the shop's staff | staff, on the admin's door | E40, E66 |

## Entities

| Entity | What it is to a user | Fields | Findings |
|---|---|---|---|
| product | what they browse and buy | slug, name, category, price, old price, stock, rating, reviews, SKU | E13, E73 |
| cart | what they are about to buy | lines, code, subtotal, delivery, total | E21, E22 |
| order | what they bought, and where it stands | number, date, lines, total, status, address | E35, E36, E72 |
| customer | who they are to the shop | email, password, name, phone, address | E28, E34 |

## Lifecycles

| Entity | From | Event | To | Findings |
|---|---|---|---|---|
| order | placed | paid | paid | E65 |
| order | paid | shipped | shipped | E65 |
| order | shipped | delivered | delivered | E65 |
| order | placed or paid | cancelled | cancelled | E37, E41 |
| product | in | three or fewer left | low | E16 |
| product | low | none left | out | E15 |

## Rules

| Rule | Except | Findings |
|---|---|---|
| up to five of a product in the cart | | E14, E61 |
| delivery free from €50, €4.90 under | | E23 |
| an order moves forward only; the customer cancels while placed | the admin also while paid | E41, E65 |
| a product out of stock is not sold | | E15, E63 |
| a password is eight characters with a number | | E30, E69 |

## Calculations

| What | How | Findings |
|---|---|---|
| a line's total | price times quantity | E21 |
| the delivery | free on a subtotal of €50 or more, else €4.90 | E23 |
| the total | subtotal, less the code, plus the delivery | E22 |

## Roles

| Role | Who | Findings |
|---|---|---|
| visitor | anyone not signed in | E5 |
| customer | signed in to their account | E5, E71 |
| admin | the warehouse's staff | E5, E66 |

## Unknowns

- How long a visitor's cart is kept before they sign in: no finding says (E20).
- What the admin may do with a paid or a shipped order: only a placed one was seen (E39).
