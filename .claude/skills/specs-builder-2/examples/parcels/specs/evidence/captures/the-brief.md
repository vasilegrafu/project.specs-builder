# The product owner's brief, 2026-10-11

- **Given:** 2026-10-11, by Ines, the product owner of the Parcelpost API, pasted into the conversation
- **Redacted:** nothing: the brief names no integrator and no recipient

We are rebuilding the Parcelpost API on the courier's new platform during the first half of 2027, and the shops that call it must not notice the move. Please write down what the API does today, call by call and event by event, so that the platform team builds the same API and we can hold them to it.

What goes wrong today, from the integrators' tickets of the third quarter of 2026:

- 23 of the 140 tickets from integrators were about webhooks they never received. In most of them the subscription had been paused after ten failures, and nobody on their side had noticed until a customer asked where a parcel was.
- 9 labels were produced for shipments that had already been cancelled, before the fix of August. The parcels reached a depot with no shipment behind them and had to be sent back by hand. Since the fix the API refuses it, and that must stay so.
- A new integrator takes a median of 6 working days from getting their key to their first label with a live key, by our onboarding log. Most of the time goes on the limits they meet one refusal at a time.

What should be better afterwards: tickets about missed webhooks under 5 a quarter by the second quarter of 2027; no label at all for a cancelled shipment; the first label within 2 working days of the key, by June 2027.

Who uses it: the integrator, the developer at a shop or at an agency who connects the shop to us and holds the key with every scope; the shop's own site, which shows the tracking to its customers with a key that may only read; and the courier's depots, whose feed moves each shipment once the parcel is handed over.

Wanted, though the rebuild stands without it: an email to the account's technical contact when a subscription is paused, so that it is noticed the same day.

Not now: resuming a paused subscription from the API. An integrator stops it and subscribes again, which gives a new secret; that is enough for the rebuild. Returns are booked with the depot by phone and stay so. No pages: the shops show the tracking on their own sites. Nothing over 30 kg: that is freight.

The description at /openapi.json is written by the server from its routes; read it as the API itself, not as someone's notes about it.
