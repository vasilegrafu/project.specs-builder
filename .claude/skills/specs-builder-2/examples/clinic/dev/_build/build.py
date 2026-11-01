#!/usr/bin/env python3
"""Write every page of the Larkfield Clinic site from clinic.json: HTML and CSS alone, every state a page of its own.

    python _build/build.py          # run from dev/: writes the pages, the styles and the pictures beside this folder

The site stands in for a clinic's site on the internet, for the specs-builder skill to walk: the home page, the
doctors, booking a visit with its refusals, the patient's visits and cancelling one, signing in, the account, the
opening hours. Nothing is sent anywhere; every form leads to the page that shows what would follow.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = json.loads((HERE / "clinic.json").read_text(encoding="utf-8"))
CLINIC = DATA["clinic"]
PATIENT = DATA["patient"]
DOCTORS = {d["slug"]: d for d in DATA["doctors"]}
VISITS = DATA["visits"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def day(date: str) -> str:
    y, m, d = date.split("-")
    return f"{int(d)} {MONTHS[int(m) - 1]} {y}"


def page(path: str, title: str, body: str, signed_in: bool = False, lead: str = "") -> None:
    depth = path.count("/")
    up = "../" * depth
    if signed_in:
        account = (f'<nav class="account-nav" aria-label="Your account"><a href="{up}visits.html">My visits</a>'
                   f'<a href="{up}account.html">{esc(PATIENT["name"].split()[0])}</a>'
                   f'<a class="btn btn-ghost" href="{up}signed-out.html">Sign out</a></nav>')
    else:
        account = (f'<nav class="account-nav" aria-label="Your account"><a href="{up}sign-in.html">Sign in</a>'
                   f'<a class="btn btn-primary" href="{up}book.html">Book a visit</a></nav>')
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · {esc(CLINIC['name'])}</title>
<link rel="stylesheet" href="{up}css/clinic.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head"><div class="wrap bar">
<a class="logo" href="{up}index.html"><img src="{up}img/logo.svg" alt="" width="32" height="32">{esc(CLINIC['name'])}</a>
<nav class="main-nav" aria-label="The clinic">
<a href="{up}doctors/index.html">Doctors</a>
<a href="{up}book.html">Book a visit</a>
<a href="{up}hours.html">Opening hours</a>
<a href="{up}contact.html">Contact</a>
</nav>
{account}
</div></header>
<main id="main" class="wrap">
{body}
</main>
<footer class="site-foot"><div class="wrap">
<p><strong>{esc(CLINIC['name'])}</strong> · {esc(CLINIC['address'])} · {esc(CLINIC['phone'])}</p>
<nav aria-label="About the site"><a href="{up}hours.html">Opening hours</a><a href="{up}privacy.html">Privacy</a><a href="{up}contact.html">Contact</a></nav>
<p class="fine">In an emergency call 999. Demo site: no visit is booked and nothing is sent.</p>
</div></footer>
</body>
</html>
"""
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8", newline="\n")


def head(title: str, lead: str = "") -> str:
    return (f'<header class="page-head"><h1>{esc(title)}</h1>'
            + (f'<p class="lead">{esc(lead)}</p>' if lead else "") + "</header>")


def doctor_card(d: dict, up: str) -> str:
    return (f'<li class="card"><img src="{up}img/{d["slug"]}.svg" alt="" width="96" height="96">'
            f'<h3><a href="{up}doctors/{d["slug"]}.html">{esc(d["name"])}</a></h3>'
            f'<p class="role">{esc(d["role"])}</p><p class="days">{esc(d["days"])}</p></li>')


def status_chip(status: str) -> str:
    words = {"booked": "Booked", "attended": "Attended", "cancelled": "Cancelled"}
    return f'<span class="status {status}">{words[status]}</span>'


# --- the pages ---------------------------------------------------------------------------------------------------

def home() -> None:
    hours = "".join(f"<tr><th scope=\"row\">{d}</th><td>{h}</td></tr>" for d, h in CLINIC["hours"][:3])
    news = "".join(f'<li><time datetime="{n["date"]}">{day(n["date"])}</time><h3>{esc(n["title"])}</h3>'
                   f'<p>{esc(n["text"])}</p></li>' for n in DATA["news"])
    cards = "".join(doctor_card(d, "") for d in list(DOCTORS.values())[:3])
    page("index.html", "Home", f"""
<section class="hero"><div><p class="kicker">{esc(CLINIC['tagline'])}</p><h1>See a doctor this week</h1>
<p>Book a visit with the doctor or nurse of your choice, see your visits, and cancel one when plans change.</p>
<p><a class="btn btn-primary big" href="book.html">Book a visit</a> <a class="btn btn-ghost big" href="doctors/index.html">Meet the doctors</a></p></div>
<div class="today card-plain"><h2>Open today</h2><p class="big-time">08:00 – 18:30</p>
<table class="hours"><tbody>{hours}</tbody></table><p><a href="hours.html">All opening hours</a></p></div></section>
<section aria-labelledby="docs-h"><h2 id="docs-h">The doctors</h2><ul class="tiles">{cards}</ul><p><a href="doctors/index.html">All six of the team</a></p></section>
<section aria-labelledby="news-h"><h2 id="news-h">News</h2><ul class="news">{news}</ul></section>
""")


def doctors() -> None:
    cards = "".join(doctor_card(d, "../") for d in DOCTORS.values())
    page("doctors/index.html", "Doctors", head("The doctors", "Six of us: four doctors, a nurse and a physiotherapist.")
         + f'<ul class="tiles">{cards}</ul>')
    for d in DOCTORS.values():
        slots = "".join(f"<li>{s}</li>" for s in d["slots"])
        page(f"doctors/{d['slug']}.html", d["name"], f"""
<nav class="crumbs" aria-label="You are here"><ol><li><a href="../index.html">Home</a></li><li><a href="index.html">Doctors</a></li><li aria-current="page">{esc(d['name'])}</li></ol></nav>
<article class="doctor"><img src="../img/{d['slug']}.svg" alt="" width="160" height="160">
<div><h1>{esc(d['name'])}</h1><p class="role">{esc(d['role'])} · {esc(d['days'])}</p><p>{esc(d['bio'])}</p>
<p><a class="btn btn-primary" href="../book.html?doctor={d['slug']}">Book a visit with {esc(d['name'].split()[-1] if d['name'].startswith('Dr') else d['name'].split()[0])}</a></p></div></article>
<section aria-labelledby="slots-h"><h2 id="slots-h">Usual times</h2><p>The times a visit starts on a working day; which are free shows when you book.</p><ul class="slots">{slots}</ul></section>
""")


def book_form(doctor: str = "", date: str = "", time: str = "", reason: str = "", email: str = "",
              errors: dict[str, str] | None = None, action: str = "booked.html") -> str:
    errors = errors or {}

    def field(name: str, label: str, control: str) -> str:
        msg = errors.get(name)
        note = f'<span class="msg" id="{name}-msg">{esc(msg)}</span>' if msg else ""
        return f'<p><label for="{name}">{label}</label>{control}{note}</p>'

    def mark(name: str) -> str:
        return f' aria-invalid="true" class="is-invalid" aria-describedby="{name}-msg"' if name in errors else ""

    options = '<option value="">Choose</option>' + "".join(
        f'<option value="{d["slug"]}"{" selected" if d["slug"] == doctor else ""}>{esc(d["name"])} · {esc(d["role"])}</option>'
        for d in DOCTORS.values())
    times = '<option value="">Choose</option>' + "".join(
        f'<option{" selected" if t == time else ""}>{t}</option>' for t in ["08:00", "08:30", "09:00", "09:30", "10:00",
                                                                          "10:30", "11:00", "11:30", "14:00", "14:30",
                                                                          "15:00", "15:30", "16:00"])
    return f"""<form class="form" action="{action}" method="get">
<fieldset><legend>Who and when</legend>
{field('doctor', 'Doctor or nurse', f'<select id="doctor" name="doctor"{mark("doctor")}>{options}</select>')}
{field('date', 'Day', f'<input id="date" name="date" type="date" value="{date}" min="2026-10-12" max="2027-01-12"{mark("date")}>')}
{field('time', 'Time', f'<select id="time" name="time"{mark("time")}>{times}</select>')}
</fieldset>
<fieldset><legend>About the visit</legend>
{field('reason', 'What is it about?', f'<textarea id="reason" name="reason" rows="3" maxlength="200"{mark("reason")}>{esc(reason)}</textarea><span class="hint">Up to 200 characters. Not for emergencies: call 999.</span>')}
{field('email', 'Your email', f'<input id="email" name="email" type="email" autocomplete="email" value="{esc(email)}"{mark("email")}>')}
</fieldset>
<button type="submit" class="btn btn-primary">Book the visit</button> <a href="index.html">Cancel</a>
</form>"""


def booking() -> None:
    page("book.html", "Book a visit", head("Book a visit", "Choose who you want to see and when. We confirm by email.")
         + book_form())
    page("book-errors.html", "Book a visit", head("Book a visit", "Choose who you want to see and when. We confirm by email.")
         + '<p class="banner error" role="alert">Three things need a look before the visit can be booked.</p>'
         + book_form(doctor="tom-hale", date="2026-10-03", time="", reason="Knee still sore after the fall", email="priya@",
                     errors={"date": "That day has passed. Choose a day from tomorrow on.",
                             "time": "Choose a time.",
                             "email": "That is not an email address."}, action="book-errors.html"))
    page("book-full.html", "Book a visit", head("Book a visit", "Choose who you want to see and when. We confirm by email.")
         + '<p class="banner notice" role="status">Dr Tom Hale has no free time on 20 October 2026. The nearest free times are on 23 October: 10:30 and 15:00.</p>'
         + book_form(doctor="tom-hale", date="2026-10-20", time="10:30", reason="Knee still sore after the fall",
                     email="priya@example.com", action="book-full.html"))
    v = VISITS[0]
    d = DOCTORS[v["doctor"]]
    page("booked.html", "Your visit is booked", f"""
{head('Your visit is booked')}
<div class="confirm card-plain"><p class="kicker">Visit {v['number']}</p>
<dl class="facts"><dt>With</dt><dd>{esc(d['name'])}, {esc(d['role'].lower())}</dd><dt>When</dt><dd>{day(v['date'])} at {v['time']}</dd><dt>About</dt><dd>{esc(v['reason'])}</dd><dt>Where</dt><dd>{esc(CLINIC['address'])}</dd></dl>
<p>We have sent the details to {esc(PATIENT['email'])}. Arrive five minutes early; bring any medicines you take.</p>
<p><a class="btn btn-primary" href="visits.html">My visits</a> <a class="btn btn-ghost" href="visits/{v['number']}.html">See this visit</a></p></div>
""", signed_in=True)


def visits() -> None:
    def rows(items: list[dict], up: str) -> str:
        return "".join(f'<tr><td><a href="{up}visits/{v["number"]}.html">{v["number"]}</a></td><td>{day(v["date"])}, {v["time"]}</td>'
                       f'<td>{esc(DOCTORS[v["doctor"]]["name"])}</td><td>{esc(v["reason"])}</td><td>{status_chip(v["status"])}</td></tr>'
                       for v in items)
    upcoming = [v for v in VISITS if v["status"] == "booked"]
    past = [v for v in VISITS if v["status"] != "booked"]
    table = ('<table class="visits"><thead><tr><th scope="col">Visit</th><th scope="col">When</th><th scope="col">With</th>'
             '<th scope="col">About</th><th scope="col">Status</th></tr></thead><tbody>{rows}</tbody></table>')
    page("visits.html", "My visits", head("My visits")
         + f'<section aria-labelledby="up-h"><h2 id="up-h">Coming up</h2>{table.format(rows=rows(upcoming, ""))}'
         + '<p><a class="btn btn-primary" href="book.html">Book another visit</a></p></section>'
         + f'<section aria-labelledby="past-h"><h2 id="past-h">Past visits</h2>{table.format(rows=rows(past, ""))}</section>',
         signed_in=True)
    page("visits-empty.html", "My visits", head("My visits")
         + '<section aria-labelledby="up-h"><h2 id="up-h">Coming up</h2><p class="empty">No visits booked. Your next one shows here once it is booked.</p>'
         + '<p><a class="btn btn-primary" href="book.html">Book a visit</a></p></section>', signed_in=True)
    for v in VISITS:
        d = DOCTORS[v["doctor"]]
        if v["status"] == "booked":
            actions = (f'<p><a class="btn btn-danger" href="{v["number"]}-cancel.html">Cancel this visit</a> '
                       f'<a class="btn btn-ghost" href="../book.html?doctor={d["slug"]}">Book another with {esc(d["name"])}</a></p>'
                       '<p class="note">A visit can be cancelled up to 24 hours before it starts; later, call the clinic.</p>')
        elif v["status"] == "attended":
            actions = '<p class="note">This visit has taken place. Nothing more to do with it.</p>'
        else:
            actions = '<p class="note">This visit was cancelled on 12 August 2026.</p>'
        page(f"visits/{v['number']}.html", f"Visit {v['number']}", f"""
<p class="crumb-line"><a href="../visits.html">My visits</a> › {v['number']}</p>
{head(f"Visit {v['number']}")}
<div class="visit card-plain"><p>{status_chip(v['status'])}</p>
<dl class="facts"><dt>With</dt><dd><a href="../doctors/{d['slug']}.html">{esc(d['name'])}</a>, {esc(d['role'].lower())}</dd><dt>When</dt><dd>{day(v['date'])} at {v['time']}</dd><dt>About</dt><dd>{esc(v['reason'])}</dd><dt>Where</dt><dd>{esc(CLINIC['address'])}</dd></dl>
{actions}</div>
""", signed_in=True)
        if v["status"] == "booked":
            page(f"visits/{v['number']}-cancel.html", f"Cancel visit {v['number']}?", f"""
<p class="crumb-line"><a href="../visits.html">My visits</a> › <a href="{v['number']}.html">{v['number']}</a> › Cancel</p>
{head(f"Cancel visit {v['number']}?")}
<div class="confirm card-plain"><p>Your visit with {esc(d['name'])} on {day(v['date'])} at {v['time']} will be cancelled and the time given to someone else. This cannot be undone.</p>
<form action="../cancelled.html" method="get"><input type="hidden" name="visit" value="{v['number']}">
<button type="submit" class="btn btn-danger">Cancel the visit</button> <a class="btn btn-ghost" href="{v['number']}.html">Keep it</a></form></div>
""", signed_in=True)
    v = VISITS[0]
    page("cancelled.html", "Visit cancelled", head("Visit cancelled")
         + f'<div class="confirm card-plain"><p>Visit {v["number"]} with {esc(DOCTORS[v["doctor"]]["name"])} on {day(v["date"])} is cancelled. We have sent a note to {esc(PATIENT["email"])}.</p>'
         '<p><a class="btn btn-primary" href="book.html">Book another visit</a> <a class="btn btn-ghost" href="visits.html">My visits</a></p></div>',
         signed_in=True)


def account() -> None:
    def sign_in_form(email: str = "", refused: bool = False) -> str:
        banner = '<p class="banner error" role="alert">The email or the password is wrong.</p>' if refused else ""
        mark = ' aria-invalid="true" class="is-invalid"' if refused else ""
        return f"""<div class="narrow">{head('Sign in', 'See your visits and book new ones.')}{banner}
<form class="form" action="{'sign-in-refused.html' if refused else 'visits.html'}" method="get">
<p><label for="email">Email</label><input id="email" name="email" type="email" autocomplete="email" required value="{esc(email)}"{mark}></p>
<p><label for="password">Password</label><input id="password" name="password" type="password" autocomplete="current-password" required{mark}></p>
<p><label><input type="checkbox" name="keep" value="1"> Keep me signed in on this device</label></p>
<button type="submit" class="btn btn-primary wide">Sign in</button>
<p class="note">First visit? <a href="book.html">Book one</a> and we set up your account. <a href="contact.html">Forgotten your password?</a></p>
</form></div>"""
    page("sign-in.html", "Sign in", sign_in_form())
    page("sign-in-refused.html", "Sign in", sign_in_form(email=PATIENT["email"], refused=True))
    page("signed-out.html", "Signed out", '<div class="narrow">' + head("You are signed out")
         + '<p>Thanks for visiting. <a href="sign-in.html">Sign in again</a> or go to the <a href="index.html">home page</a>.</p></div>')
    p = PATIENT
    page("account.html", "My account", f"""<div class="narrow">{head('My account', 'What we hold about you, and how we reach you.')}
<form class="form" action="account.html" method="get">
<p><label for="name">Full name</label><input id="name" name="name" value="{esc(p['name'])}" required></p>
<p><label for="born">Date of birth</label><input id="born" name="born" type="date" value="{p['born']}" required></p>
<p><label for="email">Email</label><input id="email" name="email" type="email" value="{esc(p['email'])}" required></p>
<p><label for="phone">Phone</label><input id="phone" name="phone" type="tel" value="{esc(p['phone'])}"><span class="hint">For reminders the day before a visit.</span></p>
<button type="submit" class="btn btn-primary">Save</button>
</form>
<p class="note">To change your name or date of birth, bring an ID to the front desk. To close your account, <a href="contact.html">write to us</a>.</p></div>
""", signed_in=True)


def information() -> None:
    rows = "".join(f'<tr><th scope="row">{d}</th><td>{h}</td></tr>' for d, h in CLINIC["hours"])
    page("hours.html", "Opening hours", head("Opening hours")
         + f'<table class="hours wide"><tbody>{rows}</tbody></table>'
         '<h2>When we are closed</h2><p>Call 111 for advice that cannot wait until we open, and 999 in an emergency. '
         'The pharmacy on Mill Lane is open until 22:00 every day.</p>'
         '<h2>Bank holidays</h2><p>Closed, with a note on this page the week before.</p>')
    page("contact.html", "Contact", head("Contact us")
         + f'<dl class="facts"><dt>Address</dt><dd>{esc(CLINIC["address"])}</dd><dt>Phone</dt><dd>{esc(CLINIC["phone"])}, '
           f'{CLINIC["hours"][0][1]} on weekdays</dd><dt>Email</dt><dd><a href="mailto:{CLINIC["email"]}">{CLINIC["email"]}</a></dd></dl>'
         '<h2>Getting here</h2><p>Larkfield station is a six-minute walk. Buses 12 and 40 stop at Mill Lane. There is step-free access from the car park, and a lift to the first floor.</p>'
         '<h2>Prescriptions</h2><p>Ask for a repeat prescription at the front desk or by phone; allow two working days.</p>')
    page("privacy.html", "Privacy", head("Privacy")
         + '<p>We keep your name, date of birth, contact details and the record of your visits, as the law on medical records requires, for as long as you are a patient and ten years after.</p>'
         '<p>We send email and text messages only about your visits: a confirmation when one is booked, a reminder the day before, and a note when one is cancelled. We never pass your details to anyone outside the practice without your consent, except where the law requires it.</p>'
         '<p>To see what we hold, or to have it corrected, <a href="contact.html">write to us</a>.</p>')


# --- the look -----------------------------------------------------------------------------------------------------

CSS = """/* Larkfield Clinic: the site's one style sheet. Calm greens, a serif for headings, one column on a phone. */
:root { --green: #1b6e53; --green-dark: #124b38; --green-pale: #e6f2ed; --ink: #1d2b26; --muted: #5d6b66;
  --line: #d6ded9; --bg: #f7faf8; --surface: #ffffff; --bad: #b42318; --bad-pale: #fdecea; --notice: #8a5a00;
  --notice-pale: #fff4dd; --radius: 8px; --font: "Segoe UI", system-ui, sans-serif; --serif: Georgia, "Times New Roman", serif; }
* { box-sizing: border-box; }
body { margin: 0; font: 16px/1.55 var(--font); color: var(--ink); background: var(--bg); }
a { color: var(--green); }
a:hover { color: var(--green-dark); }
h1, h2, h3 { font-family: var(--serif); font-weight: 600; line-height: 1.2; margin: 0 0 .5em; }
h1 { font-size: 2rem; } h2 { font-size: 1.4rem; margin-top: 1.5em; } h3 { font-size: 1.1rem; }
.wrap { max-width: 1040px; margin: 0 auto; padding: 0 20px; }
.skip { position: absolute; left: -999px; top: 0; background: var(--green); color: #fff; padding: 8px 12px; }
.skip:focus { left: 8px; z-index: 10; }
.site-head { background: var(--surface); border-bottom: 1px solid var(--line); }
.bar { display: flex; align-items: center; gap: 24px; min-height: 64px; flex-wrap: wrap; }
.logo { display: inline-flex; align-items: center; gap: 10px; font-family: var(--serif); font-size: 1.25rem; color: var(--ink); text-decoration: none; }
.main-nav { display: flex; gap: 20px; flex: 1; }
.main-nav a, .account-nav a { text-decoration: none; color: var(--ink); }
.main-nav a:hover, .account-nav a:hover { color: var(--green); text-decoration: underline; }
.account-nav { display: flex; gap: 16px; align-items: center; }
main { padding: 24px 20px 48px; }
.btn { display: inline-block; padding: 8px 16px; border-radius: var(--radius); border: 1px solid var(--green); text-decoration: none; font: inherit; cursor: pointer; line-height: 1.4; }
.btn-primary { background: var(--green); color: #fff; }
.btn-primary:hover { background: var(--green-dark); border-color: var(--green-dark); color: #fff; }
.btn-ghost { background: var(--surface); color: var(--green); }
.btn-ghost:hover { background: var(--green-pale); }
.btn-danger { background: var(--surface); color: var(--bad); border-color: var(--bad); }
.btn-danger:hover { background: var(--bad); color: #fff; }
.btn.big { padding: 12px 22px; font-size: 1.05rem; }
.btn.wide { width: 100%; }
.btn:focus-visible, a:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible { outline: 3px solid #7fc8ac; outline-offset: 2px; }
.hero { display: grid; grid-template-columns: 1.4fr 1fr; gap: 32px; align-items: start; padding: 24px 0; }
.kicker { text-transform: uppercase; letter-spacing: .08em; font-size: .8rem; color: var(--muted); margin: 0 0 4px; }
.card-plain { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 20px 24px; }
.big-time { font-size: 1.8rem; font-family: var(--serif); margin: 0 0 8px; }
table { border-collapse: collapse; }
.hours th { text-align: left; font-weight: 500; padding: 4px 16px 4px 0; }
.hours td { padding: 4px 0; }
.hours.wide { width: 100%; max-width: 480px; background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); }
.hours.wide th, .hours.wide td { padding: 10px 16px; border-bottom: 1px solid var(--line); }
.tiles { list-style: none; padding: 0; margin: 0; display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 20px; text-align: center; }
.card img { border-radius: 50%; margin-bottom: 8px; }
.card h3 { margin: 0 0 2px; }
.card h3 a { text-decoration: none; color: var(--ink); }
.card h3 a:hover { color: var(--green); text-decoration: underline; }
.role { color: var(--muted); margin: 0; }
.days { margin: 4px 0 0; font-size: .95rem; }
.news { list-style: none; padding: 0; margin: 0; display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.news li { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 16px 20px; }
.news time { color: var(--muted); font-size: .9rem; }
.news h3 { margin: 4px 0; }
.crumbs ol, .crumb-line { list-style: none; padding: 0; margin: 0 0 16px; display: flex; gap: 8px; color: var(--muted); font-size: .95rem; }
.crumbs li + li::before { content: "›"; margin-right: 8px; }
.doctor { display: grid; grid-template-columns: 160px 1fr; gap: 28px; align-items: start; background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 24px; }
.doctor img { border-radius: 50%; }
.slots { list-style: none; padding: 0; display: flex; flex-wrap: wrap; gap: 8px; }
.slots li { border: 1px solid var(--line); border-radius: 999px; padding: 4px 12px; background: var(--surface); }
.page-head { margin-bottom: 20px; }
.lead { color: var(--muted); font-size: 1.1rem; margin: 0; }
.form { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 24px; max-width: 640px; }
.form fieldset { border: 0; padding: 0; margin: 0 0 20px; }
.form legend { font-family: var(--serif); font-size: 1.2rem; margin-bottom: 8px; }
.form p { margin: 0 0 14px; }
.form label { display: block; font-weight: 600; margin-bottom: 4px; }
.form input:not([type=checkbox]), .form select, .form textarea { width: 100%; font: inherit; padding: 8px 10px; border: 1px solid var(--line); border-radius: 6px; background: var(--surface); color: var(--ink); }
.form input[type=checkbox] { margin-right: 6px; }
.form label:has(input[type=checkbox]) { font-weight: 400; }
.is-invalid { border-color: var(--bad) !important; }
.msg { display: block; color: var(--bad); font-size: .95rem; margin-top: 4px; }
.hint { display: block; color: var(--muted); font-size: .9rem; margin-top: 4px; }
.banner { padding: 12px 16px; border-radius: var(--radius); margin: 0 0 16px; max-width: 640px; }
.banner.error { background: var(--bad-pale); color: var(--bad); border: 1px solid #f0b4ad; }
.banner.notice { background: var(--notice-pale); color: var(--notice); border: 1px solid #f1d59a; }
.narrow { max-width: 480px; }
.note { color: var(--muted); font-size: .95rem; }
.empty { color: var(--muted); font-style: italic; }
.visits { width: 100%; background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); }
.visits th, .visits td { text-align: left; padding: 10px 14px; border-bottom: 1px solid var(--line); }
.visits th { color: var(--muted); font-weight: 600; font-size: .9rem; }
.visits tbody tr:hover { background: var(--green-pale); }
.status { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: .85rem; }
.status.booked { background: var(--green-pale); color: var(--green-dark); }
.status.attended { background: #e9ecef; color: #495057; }
.status.cancelled { background: var(--bad-pale); color: var(--bad); }
.facts { display: grid; grid-template-columns: 100px 1fr; gap: 6px 16px; margin: 12px 0; }
.facts dt { color: var(--muted); }
.facts dd { margin: 0; }
.confirm, .visit { max-width: 640px; }
.site-foot { border-top: 1px solid var(--line); background: var(--surface); padding: 24px 0; color: var(--muted); font-size: .95rem; }
.site-foot nav { display: flex; gap: 16px; margin: 8px 0; }
.fine { font-size: .85rem; }
@media (max-width: 800px) {
  .hero, .doctor { grid-template-columns: 1fr; }
  .tiles, .news { grid-template-columns: 1fr 1fr; }
  .main-nav { order: 3; flex-basis: 100%; }
}
@media (max-width: 480px) {
  .tiles, .news { grid-template-columns: 1fr; }
  .bar { gap: 12px; }
  .main-nav { gap: 12px; flex-wrap: wrap; }
  .visits thead { display: none; }
  .visits, .visits tbody, .visits tr, .visits td { display: block; }
  .visits tr { padding: 8px 0; border-bottom: 1px solid var(--line); }
  .visits td { border: 0; padding: 2px 14px; }
  .facts { grid-template-columns: 1fr; }
}
"""


def pictures() -> None:
    (ROOT / "img").mkdir(exist_ok=True)
    (ROOT / "img/logo.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><circle cx="16" cy="16" r="15" fill="#1b6e53"/>'
        '<path d="M16 8v16M8 16h16" stroke="#fff" stroke-width="4" stroke-linecap="round"/></svg>\n',
        encoding="utf-8", newline="\n")
    colours = ["#1b6e53", "#2f6f9f", "#8a5a00", "#6b4c9a", "#b42318", "#2b7a78"]
    for colour, d in zip(colours, DOCTORS.values()):
        initials = "".join(w[0] for w in d["name"].replace("Dr ", "").split()[:2])
        (ROOT / f"img/{d['slug']}.svg").write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 160"><circle cx="80" cy="80" r="80" fill="{colour}"/>'
            f'<text x="80" y="96" text-anchor="middle" font-family="Georgia, serif" font-size="56" fill="#fff">{initials}</text></svg>\n',
            encoding="utf-8", newline="\n")


def main() -> None:
    (ROOT / "css").mkdir(exist_ok=True)
    (ROOT / "css/clinic.css").write_text(CSS, encoding="utf-8", newline="\n")
    pictures()
    home()
    doctors()
    booking()
    visits()
    account()
    information()
    (ROOT / "robots.txt").write_text("User-agent: *\nDisallow:\n", encoding="utf-8", newline="\n")
    print(f"written: {len(list(ROOT.rglob('*.html')))} pages")


if __name__ == "__main__":
    main()
