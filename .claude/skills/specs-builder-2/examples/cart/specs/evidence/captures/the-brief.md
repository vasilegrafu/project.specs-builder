# The lead engineer's brief, 2026-10-11

- **Given:** 2026-10-11, by Mira, the shop's lead engineer, pasted into the conversation; her answers to the first reading below it, the same day
- **Redacted:** nothing: the notes name no customer

The cart is leaving the shop's one service. From January 2027 it is a service of its own, and a new cart team of three owns it. Before we split it, I want its boundary written: what the cart does, what calls it and what it calls, what it owns and what it only reads, and what it must never do. The catalogue, accounts and orders teams have to know what they can count on, and the cart team what it may not touch.

What goes wrong today. Carts lost at sign-in: support hears from about 9 customers a week who filled a cart, signed in, and found it empty or not what they had put in, September 2026. Codes that fail: of every 100 codes typed into the cart's code box, 31 are refused, by the cart's own counter in September 2026; most were typed with a space inside, or had expired.

What should be better: lost carts under 2 a week, and refused codes under 15 of 100, both by March 2027. And the split must break nothing: no call from the pages, accounts or orders that worked before the split fails after it because the cart answers differently.

Who calls it: the shop's pages, for visitors and for customers signed in; accounts, at sign-in; orders, at checkout; and the nightly job that lets old carts go.

Keep it as it is: five of a product, thirty products to a cart, free delivery from 50 euros, one code at a time. The codes stay the marketing team's; the cart reads them. Stock stays the catalogue's.

Not now: a cart saved for later or shared, and codes that stack.

Speed: the pages need a cart call answered within 300 ms today, and the same after the split.

## Her answers, after the first reading

- A visitor's cart is meant to last 48 hours; that is what we told support. If the code keeps it longer, the code is wrong.
- At sign-in the carried cart keeps to the cart's limits: five of a product, thirty products. Lines past the thirtieth are not carried.
- A code applied before its date holds until the cart is checked out: the customer saw it applied.
- The cart's answer loses which code is applied: the amount taken off is written over it. That is a slip; answer the code and its percent beside the amount, under a name of their own.
- A code once per customer was an idea of marketing's; their table does not know who used a code, so not now.
- If the stock cannot be taken after the cart is closed, that is for the orders team to answer; ask them.
- The nightly job runs on the shop's scheduler today, and the cart team takes it over at the split; at what hour is for them to say.
- The risk I see: a part still calling the cart in its own process after the split, where the cart is no longer. Each of the three teams lists its calls into the cart before January, and we check the lists against this boundary.
