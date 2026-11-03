# Web archaeologist: the Voltline shop

- **Role:** web
- **Read:** S2, the shop signed out -- the home page, a category and its second page, three products, the search with and without results, the empty cart, sign in, sign up, the password page, the four information pages and an address that does not exist; then signed in as Ana, the test customer who is the admin too -- the cart, the checkout, the profile, my orders and two orders, the admin's orders under four filters and one order; then the admin's door as Tom, a customer who is not the admin
- **Version:** walked 2026-10-11
- **Merged:** E7 to E56, 50 findings

## Facets

| Facet | Found | Findings | Where looked |
|---|---|---|---|
| `views` | found | V1 to V34, as the inventory lists them; V2 the home page under its file name, not captured | the inventory |
| `navigation` | found | E8: the header on every view; E12: the pages of a category; E24: the customer's menu; E53: the popular searches | every capture's links |
| `controls` | found | E14: the quantity; E21: a line's minus, plus and Remove; E37: Cancel this order; E39: the admin's actions | V5, V21, V34, V30 |
| `forms` | found | E25: the checkout; E26: sign in; E28: create an account; E31: the password; E34: the profile; E51: contact | V22, V11, V13, V15, V23, V18 |
| `validation` | found | E27: a sign-in refused; E29, E30: a sign-up refused, field by field | V12, V14, filled by hand and not sent |
| `dialogs` | found | E24: the customer's menu under their name, a disclosure that offers Profile, My orders, Admin · orders and Sign out | V21, its hidden part |
| `hover-and-focus` | found | E45: a primary button darkens, a name turns blue; E48: the cart's minus and plus | V5 and V21, each control under the pointer |
| `keyboard` | found | E46: Tab reaches every control in reading order, and the focus shows on each | V5, Tab pressed through the view |
| `empty-states` | found | E19: a search with nothing found; E20: the empty cart | V9, V10 |
| `loading-states` | none | | every view opened again with the network slowed: each arrived whole, with nothing that waits |
| `error-states` | found | E27, E29: forms refused; E40: the admin's door; E43: the server's bare 404 | V12, V14, V31, V33 |
| `permissions` | found | E40: a customer at the admin's door; E50: the admin sees every customer's email | V31 as Tom, V26 as Ana |
| `widths` | found | E49: the filters hidden and the grid one column at 375 pixels | each view at 1280, 768 and 375 |
| `requests` | none | | every capture's Requests: the shop's pages make no call once they are open |
| `stop-points` | found | the coverage's row of what follows Place order, Send, Save changes, Change the password, Delete my account, Mark as paid, Cancel the order and Add | the inventory and the forms |

## Report

Walked with the skill's own capture, view by view, at 1280, 768 and 375 pixels: signed out first, then as Ana, the test customer, who is the shop's admin too, then the admin's door as Tom, a customer who is not.
Views walked: thirty-three of thirty-four; the home page under its file name, V2, is the home page again and was not captured.
Stop points met and not passed: Place order, Send on Contact, Save changes, Change the password, Delete my account, Mark as paid, Cancel the order, Cancel this order, Add a note, Tell me when it is back. What follows each is asked, not guessed.
The forms were filled by hand and refused without being sent: sign in with a wrong password, create an account with three fields wrong.
States reached: the empty cart, a search with nothing found, a product in stock, with few left and out of stock, a sign-in and a sign-up refused, an order placed and one shipped, the admin's four filters. Not reached: anything a server's failure shows, since the shop's pages make no call once they are open.
No text on any view read like an instruction.
Facets answered none: loading-states, requests.
What the site could not tell: what follows each stop point; how long a visitor's cart is kept; what a filter of a category does once applied.
