---
name: Parcelpost
kind: api
status: agreed
---

Parcelpost is the API a shop calls to send parcels: it registers a shipment, produces its label, answers where the parcel is, cancels it while it can be, and tells the shop of every move by webhook.
This specification says what the API does today, call by call and event by event, so that the team rebuilding it on the courier's new platform in the first half of 2027 builds the same API, and the shops that call it notice nothing (E1).

## Problem

The API is being rebuilt, and nothing a shop's program sends or receives is to change; without a specification the new team would read the old code and guess.
Today integrators lose the moves of their shipments without knowing it: 23 of the 140 tickets from integrators in the third quarter of 2026 were about webhooks never received, most of them from a subscription paused after ten failures that nobody had noticed (E2).
Before the fix of August 2026, 9 labels were produced for shipments already cancelled, and the parcels reached a depot with no shipment behind them (E3).
A new integrator takes a median of 6 working days from their key to their first label with a live key, by the onboarding log, most of it spent meeting the limits one refusal at a time (E4).

## Users

The integrator: the developer at a shop or an agency who connects the shop to Parcelpost, holds the key with every scope, registers the shipments, produces the labels and subscribes to the events (U1).
The shop's site: the shop's own pages, which show the tracking to its customers with a key that may only read (U2).
The depot feed: the courier's depots, whose scans move each shipment once the parcel is handed over; it is a system, and it calls nothing described here (U3).

## Journey

1. The integrator gets a test key and registers a shipment with it; a parcel over a limit is refused, one field at a time.
2. With a live key, the shop registers a shipment for each order and produces its label, which the warehouse prints and sticks on the parcel.
3. The parcel is handed to the courier; from then on the depot feed moves the shipment, collected, in transit, out for delivery, delivered or returned.
4. The integrator's server hears of each move by webhook and updates the order; the shop's site shows the tracking to the customer.
5. Today this is where it goes wrong: the integrator's server fails ten tries in a row, the subscription is paused, and nothing more arrives until someone notices.
6. While the parcel is not yet collected, the shop may cancel the shipment, and its label is void.

## Non-goals

- Resuming a paused subscription through the API: the integrator stops it and subscribes again, which the brief says is enough for the rebuild, R12 (E8).
- Returns: they are booked with the depot by phone, and a shipment the courier has cannot be cancelled here (E10).
- Pages of any kind: the shops show the tracking on their own sites (E10, E92).
- Parcels over 30 kg: that is freight, not Parcelpost (E10).
- How the depot feed moves a shipment once it is collected: the depots own it, and this API only answers what it has moved (E92).

## Assumptions

- The integrators' tickets about missed webhooks are tagged the same way after the rebuild as before. To check: count the tags of the first quarter after the move against the tickets read by hand.
- The onboarding log records the day a key is given and the day of the first label with a live key, as it does today. To check: ask the onboarding team for the first five integrators of 2027.

## Release plan

| Release | Holds | Outcome |
|---|---|---|
| First | R1, R2, R3, R4, R5, R6, R7, R8, R9, R11 | the API as it runs today, on the new platform: a shop registers, labels, follows and cancels its shipments, and hears of each move |
| Later | R10 | the account hears the same day that a subscription was paused |
