# V7 · Book a visit, refused

- **Address:** http://127.0.0.1:8081/book-errors.html
- **Title:** Book a visit · Larkfield Clinic
- **Captured:** 2026-10-11 15:09, at width 1280
- **Redacted:** 3 long number(s), as [redacted], by pattern; checked by eye: what shows of Priya Nair, the test patient the practice made up for this walk, is kept: her email, in a field; what the pattern took is the clinic's own phone, and the test patient's email
- **Screenshots:** shots/V7-1280.jpg, shots/V7-375.jpg
- **Captured by:** crawl.py; every screenshot is to be looked at, and one that shows a person's data removed

## On the page

link: Skip to content
region: header
link: Larkfield Clinic → /index.html
region: navigation · The clinic
link: Doctors → /doctors/index.html
link: Book a visit → /book.html
link: Opening hours → /hours.html
link: Contact → /contact.html
region: navigation · Your account
link: Sign in → /sign-in.html
link: Book a visit → /book.html
region: main
region: header
heading: Book a visit
text: Choose who you want to see and when. We confirm by email.
message: Three things need a look before the visit can be booked.
form: Who and when · GET /book-errors.html · fields: Doctor or nurse, Day, Time, What is it about?, Your email · submit: Book the visit
text: Who and when
field: Doctor or nurse (select) · options: Choose, Dr Amara Okafor · General practitioner, Dr Tom Hale · General practitioner, Dr Inês Barros · General practitioner, Sam Whitfield · Practice nurse, Dr Lena Voss · General practitioner, Ravi Menon · Physiotherapist
field: Day (date, invalid, min 2026-10-12, max 2027-01-12) · hint: That day has passed. Choose a day from tomorrow on.
text: That day has passed. Choose a day from tomorrow on.
field: Time (select, invalid) · options: Choose, 08:00, 08:30, 09:00, 09:30, 10:00, 10:30, 11:00, 11:30, 14:00, 14:30, 15:00, and 2 more · hint: Choose a time.
text: Choose a time.
text: About the visit
field: What is it about? (maxlength 200)
text: Up to 200 characters. Not for emergencies: call 999.
field: Your email (email, invalid) · hint: That is not an email address.
text: That is not an email address.
button: Book the visit
link: Cancel → /index.html
region: footer
text: Larkfield Clinic · 14 Mill Lane, Larkfield, LK2 4HP · [redacted]
region: navigation · About the site
link: Opening hours → /hours.html
link: Privacy → /privacy.html
link: Contact → /contact.html
text: In an emergency call 999. Demo site: no visit is booked and nothing is sent.

## Hidden on the page

hidden: nothing

## Requests

request: none seen

## Styles

style: body: color #1d2b26; background-color #f7faf8; font-family "Segoe UI", system-ui, sans-serif; font-size 16px; font-weight 400; line-height 24.8px
style: header "Larkfield Clinic Doctors Book a visit Op": color #1d2b26; background-color #ffffff; font-family "Segoe UI", system-ui, sans-serif; font-size 16px; font-weight 400; line-height 24.8px
style: header "Book a visitChoose who you want to see a": color #1d2b26; font-family "Segoe UI", system-ui, sans-serif; font-size 16px; font-weight 400; line-height 24.8px
style: nav "The clinic": color #1d2b26; font-family "Segoe UI", system-ui, sans-serif; font-size 16px; font-weight 400; line-height 24.8px; gap 20px
style: nav "Your account": color #1d2b26; font-family "Segoe UI", system-ui, sans-serif; font-size 16px; font-weight 400; line-height 24.8px; gap 16px
style: nav "About the site": color #5d6b66; font-family "Segoe UI", system-ui, sans-serif; font-size 15.2px; font-weight 400; line-height 23.56px; gap 16px
style: footer "Larkfield Clinic · 14 Mill Lane, Larkfie": color #5d6b66; background-color #ffffff; font-family "Segoe UI", system-ui, sans-serif; font-size 15.2px; font-weight 400; line-height 23.56px; border 1px solid #d6ded9; padding 24px 0px
style: p "Three things need a look before the visi": color #b42318; background-color #fdecea; font-family "Segoe UI", system-ui, sans-serif; font-size 16px; font-weight 400; line-height 24.8px; border 1px solid #f0b4ad; border-radius 8px; padding 12px 16px
style: h1 "Book a visit": color #1d2b26; font-family Georgia, "Times New Roman", serif; font-size 32px; font-weight 600; line-height 38.4px
style: a "Skip to content": color #ffffff; background-color #1b6e53; font-family "Segoe UI", system-ui, sans-serif; font-size 16px; font-weight 400; line-height 24.8px; padding 8px 12px
style: a "Larkfield Clinic": color #1d2b26; font-family Georgia, "Times New Roman", serif; font-size 20px; font-weight 400; line-height 31px; gap 10px
style: a "Doctors": color #1d2b26; font-family "Segoe UI", system-ui, sans-serif; font-size 16px; font-weight 400; line-height 24.8px
style: a "Book a visit": color #1d2b26; background-color #1b6e53; font-family "Segoe UI", system-ui, sans-serif; font-size 16px; font-weight 400; line-height 22.4px; border 1px solid #1b6e53; border-radius 8px; padding 8px 16px
style: a "Cancel": color #1b6e53; font-family "Segoe UI", system-ui, sans-serif; font-size 16px; font-weight 400; line-height 24.8px
style: button "Book the visit": color #ffffff; background-color #1b6e53; font-family "Segoe UI", system-ui, sans-serif; font-size 16px; font-weight 400; line-height 22.4px; border 1px solid #1b6e53; border-radius 8px; padding 8px 16px
style: select "Doctor or nurse": color #1d2b26; background-color #ffffff; font-family "Segoe UI", system-ui, sans-serif; font-size 16px; font-weight 400; border 1px solid #d6ded9; border-radius 6px; padding 8px 10px
style: input "Day": color #1d2b26; background-color #ffffff; font-family "Segoe UI", system-ui, sans-serif; font-size 16px; font-weight 400; line-height 24.8px; border 1px solid #b42318; border-radius 6px; padding 8px 10px
style: select "Time": color #1d2b26; background-color #ffffff; font-family "Segoe UI", system-ui, sans-serif; font-size 16px; font-weight 400; border 1px solid #b42318; border-radius 6px; padding 8px 10px
style: textarea "What is it about?": color #1d2b26; background-color #ffffff; font-family "Segoe UI", system-ui, sans-serif; font-size 16px; font-weight 400; line-height 24.8px; border 1px solid #d6ded9; border-radius 6px; padding 8px 10px

## After actions

### Each control under the pointer (crawl.py)

hover: Larkfield Clinic: rgb(29, 43, 38) | rgba(0, 0, 0, 0) | rgb(29, 43, 38) | none | none | 1 | pointer → rgb(18, 75, 56) | rgba(0, 0, 0, 0) | rgb(18, 75, 56) | none | none | 1 | pointer
hover: Doctors: rgb(29, 43, 38) | rgba(0, 0, 0, 0) | rgb(29, 43, 38) | none | none | 1 | pointer → rgb(27, 110, 83) | rgba(0, 0, 0, 0) | rgb(27, 110, 83) | underline | none | 1 | pointer
hover: Book a visit: rgb(29, 43, 38) | rgba(0, 0, 0, 0) | rgb(29, 43, 38) | none | none | 1 | pointer → rgb(27, 110, 83) | rgba(0, 0, 0, 0) | rgb(27, 110, 83) | underline | none | 1 | pointer
hover: Opening hours: rgb(29, 43, 38) | rgba(0, 0, 0, 0) | rgb(29, 43, 38) | none | none | 1 | pointer → rgb(27, 110, 83) | rgba(0, 0, 0, 0) | rgb(27, 110, 83) | underline | none | 1 | pointer
hover: Contact: rgb(29, 43, 38) | rgba(0, 0, 0, 0) | rgb(29, 43, 38) | none | none | 1 | pointer → rgb(27, 110, 83) | rgba(0, 0, 0, 0) | rgb(27, 110, 83) | underline | none | 1 | pointer
hover: Sign in: rgb(29, 43, 38) | rgba(0, 0, 0, 0) | rgb(29, 43, 38) | none | none | 1 | pointer → rgb(27, 110, 83) | rgba(0, 0, 0, 0) | rgb(27, 110, 83) | underline | none | 1 | pointer
hover: Book a visit: rgb(29, 43, 38) | rgb(27, 110, 83) | rgb(27, 110, 83) | none | none | 1 | pointer → rgb(27, 110, 83) | rgb(18, 75, 56) | rgb(18, 75, 56) | underline | none | 1 | pointer
hover: Book the visit: rgb(255, 255, 255) | rgb(27, 110, 83) | rgb(27, 110, 83) | none | none | 1 | pointer → rgb(255, 255, 255) | rgb(18, 75, 56) | rgb(18, 75, 56) | none | none | 1 | pointer
hover: Cancel: rgb(27, 110, 83) | rgba(0, 0, 0, 0) | rgb(27, 110, 83) | underline | none | 1 | pointer → rgb(18, 75, 56) | rgba(0, 0, 0, 0) | rgb(18, 75, 56) | underline | none | 1 | pointer
hover: Opening hours: rgb(27, 110, 83) | rgba(0, 0, 0, 0) | rgb(27, 110, 83) | underline | none | 1 | pointer → rgb(18, 75, 56) | rgba(0, 0, 0, 0) | rgb(18, 75, 56) | underline | none | 1 | pointer
hover: Privacy: rgb(27, 110, 83) | rgba(0, 0, 0, 0) | rgb(27, 110, 83) | underline | none | 1 | pointer → rgb(18, 75, 56) | rgba(0, 0, 0, 0) | rgb(18, 75, 56) | underline | none | 1 | pointer
hover: Contact: rgb(27, 110, 83) | rgba(0, 0, 0, 0) | rgb(27, 110, 83) | underline | none | 1 | pointer → rgb(18, 75, 56) | rgba(0, 0, 0, 0) | rgb(18, 75, 56) | underline | none | 1 | pointer

### Tab pressed through the view (crawl.py)

focus: 1 · a Larkfield Clinic
focus: 2 · a Doctors
focus: 3 · a Book a visit
focus: 4 · a Opening hours
focus: 5 · a Contact
focus: 6 · a Sign in
focus: 7 · a Book a visit
focus: 8 · select Choose Dr Amara Okafor · General practitioner Dr Tom Hale · General practitioner
focus: 9 · input 2026-10-03
focus: 10 · input 2026-10-03
focus: 11 · input 2026-10-03
focus: 12 · input 2026-10-03 (no focus shows)
focus: 13 · select Choose 08:00 08:30 09:00 09:30 10:00 10:30 11:00 11:30 14:00 14:30 15:00 15:30 1
focus: 14 · textarea Knee still sore after the fall
focus: 15 · input priya@
focus: 16 · button Book the visit
focus: 17 · a Cancel
focus: 18 · a Opening hours
focus: 19 · a Privacy
focus: 20 · a Contact
focus: 22 · a Skip to content

### Opened again with the network slowed (crawl.py)

text: Skip to content
text: Larkfield Clinic
text: Doctors
text: Book a visit
text: Opening hours
text: Contact
text: Sign in
text: Book a visit
text: Book a visit
text: Choose who you want to see and when. We confirm by email.
text: Three things need a look before the visit can be booked.
text: Who and when
text: Doctor or nurse
text: Choose
text: Dr Amara Okafor · General practitioner
text: Dr Tom Hale · General practitioner
text: Dr Inês Barros · General practitioner
text: Sam Whitfield · Practice nurse
text: Dr Lena Voss · General practitioner
text: Ravi Menon · Physiotherapist
text: Day
text: That day has passed. Choose a day from tomorrow on.
text: Time
text: Choose
text: 08:00
text: 08:30
text: 09:00
text: 09:30
text: 10:00
text: 10:30
text: 11:00
text: 11:30
text: 14:00
text: 14:30
text: 15:00
text: 15:30
text: 16:00
text: Choose a time.
text: About the visit
text: What is it about?

### Opened again with its calls to the server cut (crawl.py)

text: it showed what it shows with its calls answered

## Accessibility tree

```yaml
- link "Skip to content":
  - /url: #main
- banner:
  - link "Larkfield Clinic":
    - /url: index.html
  - navigation "The clinic":
    - link "Doctors":
      - /url: doctors/index.html
    - link "Book a visit":
      - /url: book.html
    - link "Opening hours":
      - /url: hours.html
    - link "Contact":
      - /url: contact.html
  - navigation "Your account":
    - link "Sign in":
      - /url: sign-in.html
    - link "Book a visit":
      - /url: book.html
- main:
  - heading "Book a visit" [level=1]
  - paragraph: Choose who you want to see and when. We confirm by email.
  - alert: Three things need a look before the visit can be booked.
  - group "Who and when":
    - text: Who and when
    - paragraph:
      - text: Doctor or nurse
      - combobox "Doctor or nurse":
        - option "Choose"
        - option "Dr Amara Okafor · General practitioner"
        - option "Dr Tom Hale · General practitioner" [selected]
        - option "Dr Inês Barros · General practitioner"
        - option "Sam Whitfield · Practice nurse"
        - option "Dr Lena Voss · General practitioner"
        - option "Ravi Menon · Physiotherapist"
    - paragraph:
      - text: Day
      - textbox "Day" [invalid]
      - text: That day has passed. Choose a day from tomorrow on.
    - paragraph:
      - text: Time
      - combobox "Time" [invalid]:
        - option "Choose" [selected]
        - option "08:00"
        - option "08:30"
        - option "09:00"
        - option "09:30"
        - option "10:00"
        - option "10:30"
        - option "11:00"
        - option "11:30"
        - option "14:00"
        - option "14:30"
        - option "15:00"
        - option "15:30"
        - option "16:00"
      - text: Choose a time.
  - group "About the visit":
    - text: About the visit
    - paragraph:
      - text: What is it about?
      - textbox "What is it about?"
      - text: "Up to 200 characters. Not for emergencies: call 999."
    - paragraph:
      - text: Your email
      - textbox "Your email" [invalid]
      - text: That is not an email address.
  - button "Book the visit"
  - link "Cancel":
    - /url: index.html
- contentinfo:
  - paragraph:
    - strong: Larkfield Clinic
    - text: · 14 Mill Lane, Larkfield, LK2 4HP · [redacted]
  - navigation "About the site":
    - link "Opening hours":
      - /url: hours.html
    - link "Privacy":
      - /url: privacy.html
    - link "Contact":
      - /url: contact.html
  - paragraph: "In an emergency call 999. Demo site: no visit is booked and nothing is sent."
```
