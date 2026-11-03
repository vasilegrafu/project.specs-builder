# Billing and pricing

- **What it is:** How the product earns money and how the money is collected. It covers what is charged for, plans and trials, taking payment, invoices and tax, and what happens when payment fails.
- **Applies when:** Someone pays for the product. It does not apply to an internal tool, or to a product paid for outside it by contract and bank transfer.
- **If left unsaid:** Nothing is built for money, and it is added after launch under pressure. Or a full subscription system is built before anyone has agreed to pay anything.
- **Ask:**
  1. Who pays: the person using it, their employer, someone else?
  2. What do they pay for -- each user, each use, a flat fee, a share of something?
  3. Have you asked anyone what they would pay, or what they pay today for the alternative?
  4. Do they pay before they have seen it work, after a trial, or after a free tier runs out?
  5. In which countries, in which currencies, and do they need an invoice their accountant accepts?
- **Options:**
  - invoice by hand -- you send an invoice and they pay by transfer; nothing to build, natural for a handful of business customers, and unworkable for many small ones.
  - a payment provider's hosted checkout -- the provider's own pages take the card, handle renewals and send receipts; little to build, and their rules and fees apply.
  - billing built into the product -- plans, upgrades, proration and invoices of your own; full control and a large, permanent piece of work.
  - free for now -- charge nothing while proving people want it; removes the area from the first release, and postpones learning whether anyone will pay.
- **First release:** Whichever is least work for the number of customers expected in the first months: by hand for a few business customers, a hosted checkout with one plan otherwise. Decide the price and what is charged for even if collection is manual, because that shapes the product. Several plans, proration and self-service changes wait.
- **Often forgotten:** A card that fails on renewal, and how long access continues. Refunds. Tax, which depends on where the customer is. What a customer keeps when they downgrade or stop paying. Who inside the customer may see and change billing. A price change for customers who already pay.
- **Becomes:** A decision on what is charged for; requirements for paying, for failed payment and for the end of a trial; a constraint from the payment provider and from tax law; an assumption about the price, with its check; non-goals for what waits.
