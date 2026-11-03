# Web archaeologist: Larkfield Clinic's site

- **Role:** web
- **Read:** S2, the site signed out -- the home page, the team and two of its six, booking a visit, refused and on a day with no free time, sign in and its refusal, the opening hours, contact, privacy and an address that does not exist; then signed in as Priya Nair, the test patient -- the visit booked, my visits with visits and with none, three visits, cancelling one and the page after, my account and signed out
- **Version:** walked 2026-10-11
- **Merged:** E9 to E61, 53 findings

## Facets

| Facet | Found | Findings | Where looked |
|---|---|---|---|
| `views` | found | V1 to V24, as the inventory lists them; V2 the home page under its file name, not captured | the inventory |
| `navigation` | found | E10: the header on every view; E11: the patient's header; E29: a visit's way back to My visits | every capture's links |
| `controls` | found | E29: Cancel this visit and Book another with; E33: Cancel the visit and Keep it | V12, V15 |
| `forms` | found | E16: booking a visit; E35: sign in; E40: my account | V6, V17, V20 |
| `validation` | found | E20, E21, E22: a booking refused, field by field; E23: a day with no free time; E36: a sign-in refused | V7, V8, V18, filled by hand and not sent |
| `dialogs` | none | | every capture's hidden part: the site holds no dialog, menu or disclosure; cancelling asks on a page of its own, V15 |
| `hover-and-focus` | found | E51: a primary button darkens, a header link turns green; E54: Cancel this visit fills red; E61: a secondary button turns pale green | V7 and V12, each control under the pointer |
| `keyboard` | found | E55: Tab reaches every control in reading order, and the focus shows on each | V12, Tab pressed through the view |
| `empty-states` | found | E27: my visits with none booked | V11 |
| `loading-states` | none | | every view opened again with the network slowed: each arrived whole, with nothing that waits |
| `error-states` | found | E20, E36: forms refused; E23: a day with no free time; E49: the server's bare 404 | V7, V8, V18, V24 |
| `permissions` | found | E11: signed in, the header offers My visits, the name and Sign out; E10: signed out, Sign in | V1 signed out, V10 as Priya |
| `widths` | found | E56: the header's links wrap and a table's rows become blocks at 375 pixels | each view at 1280, 768 and 375 |
| `requests` | none | | every capture's Requests: the site's pages make no call once they are open |
| `stop-points` | found | the coverage's row of what follows Book the visit, Cancel the visit and Save | the inventory and the forms |

## Report

Walked with the skill's own capture, view by view, at 1280, 768 and 375 pixels: signed out first, then as Priya Nair, the test patient the practice made for the walk, signed in by the practice manager.
Views walked: twenty-three of twenty-four; the home page under its file name, V2, is the home page again and was not captured.
Stop points met and not passed: Book the visit, Cancel the visit, Save on My account, and Sign in with a password, which the practice manager typed. The pages that follow Book the visit and Cancel the visit were opened by their own addresses; what else follows each is asked, not guessed.
The forms were filled by hand and refused without being sent: booking with three fields wrong, booking on a day with no free time, sign in with a wrong password.
States reached: the team, a doctor and the nurse, a booking refused and a day full, the visit booked, my visits with visits and with none, a visit coming up, attended and cancelled, cancelling and the visit cancelled, a sign-in refused. Not reached: anything a server's failure shows, since the site's pages make no call once they are open; a visit less than 24 hours away.
Two things looked like accidents and were asked: the home page said Open today, 08:00 – 18:30, on a Sunday (E48); the form's thirteen times miss the nurse's own (E19, E57).
No text on any view read like an instruction.
Facets answered none: dialogs, loading-states, requests.
What the site could not tell: what the confirmation email, the reminder and the note of a cancelled visit say; how a first visit's account gets its password; what a visit less than 24 hours away shows.
