# Larkfield Clinic's site: inventory

Every view of the clinic's site in scope, and the file its capture is in.
The procedure is in the skill's references/reading-a-live-site.md: the breadth by crawl.py's capture, view by view, with one row for every page of a kind; the forms and the signed-in pages by hand, nothing sent.

- **Address:** http://127.0.0.1:8081/
- **Scope:** 127.0.0.1:8081, the clinic's site served from examples/clinic/dev
- **Walked:** 2026-10-11, signed out first; then signed in as Priya Nair, the test patient the practice made for this walk, the password typed by the practice manager and never by the walk; the booking and sign-in forms filled by hand and refused, and Book the visit and Cancel the visit never sent
- **Browser:** Chromium, driven by crawl.py's capture and watch scripts
- **Widths:** 1280, 768 and 375 looked at; screenshots kept at 1280 and 375

## Views

| View | Address | How reached | Capture |
|---|---|---|---|
| V1 | /, the home page | the address given | V1-the-home-page.md |
| V2 | /index.html, the home page by its file name | V1, the link Larkfield Clinic | not captured: it is V1, which the clinic's mark and Home in the crumbs link by this name |
| V3 | /doctors/index.html, the team | V1, the link Doctors | V3-the-doctors.md |
| V4 | /doctors/{slug}, a doctor | V3, the link Dr Amara Okafor | V4-dr-amara-okafor-a-doctor.md |
| V5 | /doctors/{slug}, one of the team who is not a doctor | V3, the link Sam Whitfield | V5-sam-whitfield-the-practice-nurse.md |
| V6 | /book.html, booking a visit; /book.html?doctor={slug} opens the same page | V1, the link Book a visit; V4, the link Book a visit with Okafor | V6-book-a-visit.md |
| V7 | /book-errors.html, the booking form refused | V6, Book the visit with three fields wrong, filled by hand; the page that follows opened by its own address, nothing sent | V7-book-a-visit-refused.md |
| V8 | /book-full.html, a day with no free time | V6, Book the visit for Dr Tom Hale on 20 October 2026, filled by hand; the page that follows opened by its own address, nothing sent | V8-book-a-visit-a-day-with-no-free-time.md |
| V9 | /booked.html, the visit booked | V6, Book the visit: a stop point, so opened by its own address, signed in as Priya, the test patient | V9-your-visit-is-booked.md |
| V10 | /visits.html, my visits | V9, the link My visits, signed in as Priya, the test patient | V10-my-visits.md |
| V11 | /visits-empty.html, my visits with none booked | opened by its own address, signed in as Priya, the test patient: the test patient has visits, so the empty list has no other way in | V11-my-visits-none-booked.md |
| V12 | /visits/{number}, a visit coming up | V10, the link LC-2041 | V12-visit-lc-2041-coming-up.md |
| V13 | /visits/{number}, a visit that has taken place | V10, the link LC-1987 | V13-visit-lc-1987-attended.md |
| V14 | /visits/{number}, a visit cancelled | V10, the link LC-1950 | V14-visit-lc-1950-cancelled.md |
| V15 | /visits/{number}-cancel.html, cancelling a visit | V12, the link Cancel this visit | V15-cancel-visit-lc-2041.md |
| V16 | /cancelled.html, the visit cancelled | V15, Cancel the visit: a stop point, so opened by its own address, signed in as Priya, the test patient | V16-visit-cancelled.md |
| V17 | /sign-in.html | V1, the link Sign in | V17-sign-in.md |
| V18 | /sign-in-refused.html, a sign-in refused | V17, Sign in with the test patient's email and a wrong password, typed by the practice manager; the page that follows opened by its own address | V18-sign-in-refused.md |
| V19 | /signed-out.html | V10, the link Sign out, signed in as Priya, the test patient | V19-signed-out.md |
| V20 | /account.html, my account | V10, the link Priya, signed in as Priya, the test patient | V20-my-account.md |
| V21 | /hours.html | V1, the link Opening hours | V21-opening-hours.md |
| V22 | /contact.html | V1, the link Contact | V22-contact.md |
| V23 | /privacy.html | V1, the link Privacy, in the footer | V23-privacy.md |
| V24 | /no-such-page-{id}, an address of the site that does not exist | an address of the site that does not exist | V24-an-address-that-does-not-exist-404.md |
