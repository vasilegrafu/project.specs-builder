# Parcelpost

The API a shop calls to send parcels: register a shipment, produce its
label, follow it to the door, cancel it while it can be, and hear of
every move by webhook. No pages: a shop's own site shows the tracking to
its customers, and the courier's depots feed the scans.

- `parcelpost/app.py`: every route, with the limits a parcel is held to.
- `parcelpost/models.py`: a shipment and its life, its events, a subscription.
- `parcelpost/auth.py`: the API key, its account and its scopes.
- `parcelpost/webhooks.py`: what is sent, how it is signed, and how it is tried again.
- `openapi.json`: the description, as the server writes it from the routes.
- `tests/`: what the API promises.

Run it with `uvicorn parcelpost.app:app`; the description is served at
`/openapi.json`. A test key, `pp_test_7f3a9c2e`, makes shipments that are
never collected. Demo material for the specs-builder skill: nothing here
is a real courier.
