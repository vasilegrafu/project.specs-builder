#!/usr/bin/env python3
"""Writes the Voltline shop: every page, every product picture, from products.json beside this file.

    python _build/build.py          # from dev/: writes the pages, the pictures and robots.txt

The shop is a stand-in for a site on the internet, for the specs-builder skill to walk and read. It is HTML and
CSS alone, no script: each state a page of its own, reached by a link, so that a walk sees every one of them.
Standard library only."""
from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = json.loads((HERE / "products.json").read_text(encoding="utf-8"))
SHOP = DATA["shop"]
CATEGORIES = DATA["categories"]
PRODUCTS = DATA["products"]
CUSTOMER = DATA["customer"]
ORDERS = DATA["orders"]
PAGE_SIZE = 4
BY_SLUG = {p["slug"]: p for p in PRODUCTS}
BY_CATEGORY = {c["slug"]: [p for p in PRODUCTS if p["category"] == c["slug"]] for c in CATEGORIES}
CATEGORY_OF = {c["slug"]: c for c in CATEGORIES}
STATUS_WORDS = {"placed": "Placed", "paid": "Paid", "shipped": "Shipped", "delivered": "Delivered",
                "cancelled": "Cancelled"}
STATUS_ORDER = ["placed", "paid", "shipped", "delivered"]


def e(text: object) -> str:
    return escape(str(text), quote=True)


def money(amount: float) -> str:
    return f"€{amount:,.2f}"


def stars(rating: float) -> str:
    full = int(rating)
    half = rating - full >= 0.5
    drawn = "★" * full + ("½" if half else "") + "☆" * (5 - full - (1 if half else 0))
    return f'<span class="stars" aria-label="{rating} out of 5">{drawn}</span>'


# --- the frame of every page ------------------------------------------------------------------------------------
def head(title: str, up: str) -> str:
    return (f'<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{e(title)} · {e(SHOP["name"])}</title>\n'
            f'<link rel="stylesheet" href="{up}css/shop.css">\n</head>\n<body>\n'
            f'<a class="skip" href="#main">Skip to content</a>\n')


def header(up: str, signed_in: bool, current: str = "") -> str:
    out = ['<header class="site-head">', '<div class="wrap bar">',
           f'<a class="logo" href="{up}index.html"><img src="{up}img/logo.svg" alt="" width="30" height="30">'
           f'{e(SHOP["name"])}</a>',
           f'<form class="search" role="search" action="{up}search.html" method="get">'
           '<label class="sr-only" for="q">Search products</label>'
           '<input id="q" name="q" type="search" placeholder="Search products, brands and more" autocomplete="off">'
           '<button type="submit">Search</button></form>',
           '<nav class="account-nav" aria-label="Account">']
    if signed_in:
        out.append('<details class="menu"><summary>Hi, ' + e(CUSTOMER["first"]) + '</summary><ul>'
                   f'<li><a href="{up}account/profile.html">Profile</a></li>'
                   f'<li><a href="{up}account/orders.html">My orders</a></li>'
                   f'<li><a href="{up}admin/orders.html">Admin · orders</a></li>'
                   f'<li><a href="{up}signed-out.html">Sign out</a></li></ul></details>')
        out.append(f'<a class="cart" href="{up}cart.html">Cart <span class="count" aria-label="2 items">2</span></a>')
    else:
        out.append(f'<a href="{up}sign-in.html">Sign in</a>')
        out.append(f'<a class="btn btn-ghost" href="{up}sign-up.html">Sign up</a>')
        out.append(f'<a class="cart" href="{up}cart-empty.html">Cart <span class="count" aria-label="0 items">0</span></a>')
    out.append("</nav></div>")
    out.append('<nav class="cat-nav wrap" aria-label="Categories">')
    for c in CATEGORIES:
        aria = ' aria-current="page"' if c["slug"] == current else ""
        out.append(f'<a href="{up}c/{c["slug"]}/index.html"{aria}>{e(c["name"])}</a>')
    out.append("</nav></header>")
    return "\n".join(out) + "\n"


def footer(up: str) -> str:
    return (f'<footer class="site-foot"><div class="wrap">'
            f'<p><strong>{e(SHOP["name"])}</strong> · {e(SHOP["tagline"])}</p>'
            f'<nav aria-label="About the shop"><a href="{up}about.html">About</a><a href="{up}contact.html">Contact</a>'
            f'<a href="{up}terms.html">Terms</a><a href="{up}shipping.html">Shipping &amp; returns</a></nav>'
            f'<p class="fine">© 2026 {e(SHOP["name"])} GmbH. Prices include VAT. Demo shop: nothing is sold.</p>'
            f"</div></footer>\n</body>\n</html>\n")


def page(path: str, title: str, body: str, signed_in: bool = False, current: str = "") -> None:
    up = "../" * path.count("/")
    text = head(title, up) + header(up, signed_in, current) + f'<main id="main" class="wrap">\n{body}</main>\n' + footer(up)
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")


def crumbs(up: str, *trail: tuple[str, str]) -> str:
    items = [f'<li><a href="{up}index.html">Home</a></li>']
    for name, href in trail[:-1]:
        items.append(f'<li><a href="{href}">{e(name)}</a></li>')
    items.append(f'<li aria-current="page">{e(trail[-1][0])}</li>')
    return '<nav class="crumbs" aria-label="You are here"><ol>' + "".join(items) + "</ol></nav>"


# --- products ----------------------------------------------------------------------------------------------------
def stock_badge(p: dict) -> str:
    return {"in": '<span class="stock in">In stock</span>',
            "low": '<span class="stock low">Only a few left</span>',
            "out": '<span class="stock out">Out of stock</span>'}[p["stock"]]


def price_html(p: dict) -> str:
    if p.get("old_price"):
        return (f'<span class="price"><span class="now">{money(p["price"])}</span> '
                f'<s class="was">{money(p["old_price"])}</s> <span class="deal">Deal</span></span>')
    return f'<span class="price"><span class="now">{money(p["price"])}</span></span>'


def card(p: dict, up: str) -> str:
    out = ['<li class="card">',
           f'<a class="card-link" href="{up}p/{p["slug"]}.html">'
           f'<img src="{up}img/{p["slug"]}.svg" alt="{e(p["name"])}" width="400" height="300" loading="lazy">'
           f'<span class="name">{e(p["name"])}</span></a>',
           f'<p class="meta">{stars(p["rating"])} <span class="reviews">({p["reviews"]})</span></p>',
           f'<p>{price_html(p)}</p>', f'<p>{stock_badge(p)}</p>']
    if p["stock"] == "out":
        out.append('<button type="button" class="btn" disabled>Add to cart</button>')
    else:
        out.append(f'<form action="{up}cart.html" method="get"><input type="hidden" name="add" value="{e(p["slug"])}">'
                   '<button type="submit" class="btn btn-primary">Add to cart</button></form>')
    out.append("</li>")
    return "\n".join(out)


def grid(products: list[dict], up: str) -> str:
    return '<ul class="grid">\n' + "\n".join(card(p, up) for p in products) + "\n</ul>"


def category_pages() -> None:
    for c in CATEGORIES:
        items = BY_CATEGORY[c["slug"]]
        pages = [items[i:i + PAGE_SIZE] for i in range(0, len(items), PAGE_SIZE)]
        for n, shown in enumerate(pages, start=1):
            path = f"c/{c['slug']}/index.html" if n == 1 else f"c/{c['slug']}/page-{n}.html"
            up = "../../"
            nav = ['<nav class="pages" aria-label="Pages">']
            if n > 1:
                nav.append(f'<a href="{"index.html" if n == 2 else f"page-{n - 1}.html"}" rel="prev">‹ Previous</a>')
            for k in range(1, len(pages) + 1):
                href = "index.html" if k == 1 else f"page-{k}.html"
                nav.append(f'<a href="{href}" aria-current="page">{k}</a>' if k == n else f'<a href="{href}">{k}</a>')
            if n < len(pages):
                nav.append(f'<a href="page-{n + 1}.html" rel="next">Next ›</a>')
            nav.append("</nav>")
            first, last = (n - 1) * PAGE_SIZE + 1, (n - 1) * PAGE_SIZE + len(shown)
            body = (crumbs(up, (c["name"], "index.html")) +
                    f'<header class="page-head"><h1>{e(c["name"])}</h1><p class="lead">{e(c["blurb"])}</p></header>\n'
                    '<div class="toolbar"><p class="count">Showing ' + f'{first}–{last} of {len(items)} products</p>'
                    '<form class="sort" action="index.html" method="get"><label for="sort">Sort by</label>'
                    '<select id="sort" name="sort"><option>Featured</option><option>Price: low to high</option>'
                    '<option>Price: high to low</option><option>Rating</option><option>Newest</option></select>'
                    '<button type="submit" class="btn btn-ghost">Apply</button></form></div>\n'
                    '<div class="with-filters"><aside class="filters" aria-label="Filters"><h2>Filters</h2>'
                    '<fieldset><legend>Price</legend><label><input type="checkbox" name="price" value="0-200"> Under €200</label>'
                    '<label><input type="checkbox" name="price" value="200-800"> €200 to €800</label>'
                    '<label><input type="checkbox" name="price" value="800-"> Over €800</label></fieldset>'
                    '<fieldset><legend>Availability</legend><label><input type="checkbox" name="stock" value="in"> In stock only</label></fieldset>'
                    '<fieldset><legend>Rating</legend><label><input type="radio" name="rating" value="4"> 4 stars and up</label>'
                    '<label><input type="radio" name="rating" value="3"> 3 stars and up</label></fieldset></aside>\n'
                    + grid(shown, up) + "\n" + "\n".join(nav) + "</div>\n")
            page(path, f"{c['name']} · page {n}" if n > 1 else c["name"], body, current=c["slug"])


def product_pages() -> None:
    for p in PRODUCTS:
        c = CATEGORY_OF[p["category"]]
        up = "../"
        related = [r for r in BY_CATEGORY[c["slug"]] if r["slug"] != p["slug"]][:3]
        specs = "".join(f"<tr><th scope=\"row\">{e(k)}</th><td>{e(v)}</td></tr>" for k, v in p["specs"].items())
        if p["stock"] == "out":
            buy = ('<button type="button" class="btn btn-primary" disabled>Add to cart</button>'
                   '<p class="note">Out of stock. <a href="#notify">Tell me when it is back</a>.</p>')
        else:
            buy = (f'<form class="buy" action="{up}cart.html" method="get"><input type="hidden" name="add" value="{e(p["slug"])}">'
                   '<label for="qty">Quantity</label><input id="qty" name="qty" type="number" value="1" min="1" max="5">'
                   '<button type="submit" class="btn btn-primary">Add to cart</button></form>')
        body = (crumbs(up, (c["name"], f"{up}c/{c['slug']}/index.html"), (p["name"], "")) +
                '<article class="product">'
                f'<div class="gallery"><img src="{up}img/{p["slug"]}.svg" alt="{e(p["name"])}" width="400" height="300"></div>'
                '<div class="facts">'
                f'<h1>{e(p["name"])}</h1>'
                f'<p class="meta">{stars(p["rating"])} <a href="#reviews">{p["reviews"]} reviews</a> · <span class="sku">SKU {e(p["sku"])}</span></p>'
                f'<p class="big">{price_html(p)}</p>'
                f'<p>{stock_badge(p)}</p>'
                f'<p class="blurb">{e(p["blurb"])}</p>'
                + buy +
                '<ul class="promises"><li>Free delivery over €50</li><li>30-day returns</li><li>2-year warranty</li></ul>'
                '</div></article>\n'
                '<section class="specs" aria-labelledby="specs-h"><h2 id="specs-h">Specifications</h2>'
                f'<table class="specs-table">{specs}</table></section>\n'
                '<section id="reviews" aria-labelledby="reviews-h"><h2 id="reviews-h">Reviews</h2>'
                f'<p>{stars(p["rating"])} {p["rating"]} out of 5, from {p["reviews"]} reviews.</p>'
                '<ul class="reviews-list">'
                f'<li><p class="who">M. K. · verified purchase</p>{stars(5)}<p>{e(p["review"])}</p></li>'
                '</ul></section>\n'
                '<section id="notify" aria-labelledby="related-h"><h2 id="related-h">You may also like</h2>'
                + grid(related, up) + "</section>\n")
        page(f"p/{p['slug']}.html", p["name"], body, current=c["slug"])


# --- home, search ------------------------------------------------------------------------------------------------
def home() -> None:
    deals = [p for p in PRODUCTS if p.get("old_price")][:4]
    new = [p for p in PRODUCTS if p.get("new")][:4]
    tiles = "".join(f'<li><a href="c/{c["slug"]}/index.html"><img src="img/{BY_CATEGORY[c["slug"]][0]["slug"]}.svg" alt="" '
                    f'width="400" height="300"><span>{e(c["name"])}</span></a></li>' for c in CATEGORIES)
    hero = BY_SLUG[SHOP["hero"]]
    body = (f'<section class="hero"><div><p class="kicker">This week</p><h1>{e(hero["name"])}</h1>'
            f'<p>{e(hero["blurb"])}</p><p class="big">{price_html(hero)}</p>'
            f'<a class="btn btn-primary" href="p/{hero["slug"]}.html">See the deal</a></div>'
            f'<img src="img/{hero["slug"]}.svg" alt="{e(hero["name"])}" width="400" height="300"></section>\n'
            f'<section aria-labelledby="cats-h"><h2 id="cats-h">Shop by category</h2><ul class="tiles">{tiles}</ul></section>\n'
            '<section aria-labelledby="deals-h"><h2 id="deals-h">Deals this week</h2>' + grid(deals, "") + "</section>\n"
            '<section aria-labelledby="new-h"><h2 id="new-h">New arrivals</h2>' + grid(new, "") + "</section>\n"
            '<section aria-labelledby="pop-h"><h2 id="pop-h">Popular searches</h2><p class="chips">'
            '<a href="search.html?q=headphones">headphones</a><a href="search.html?q=4k+monitor">4K monitor</a>'
            '<a href="search.html?q=laptop">laptop</a><a href="search-no-results.html?q=quantum+toaster">quantum toaster</a>'
            "</p></section>\n")
    page("index.html", "Electronics with free delivery", body)


def search_pages() -> None:
    found = [p for p in PRODUCTS if p["category"] == "audio"][:5]
    body = ('<header class="page-head"><h1>Results for “headphones”</h1>'
            f'<p class="lead">{len(found)} products match.</p></header>\n' + grid(found, "") + "\n")
    page("search.html", "Search: headphones", body)
    body = ('<header class="page-head"><h1>Results for “quantum toaster”</h1>'
            '<p class="lead">Nothing matches.</p></header>\n'
            '<div class="empty"><p>Check the spelling, try fewer words, or browse a category.</p>'
            '<p class="chips"><a href="search.html?q=headphones">headphones</a><a href="c/laptops/index.html">Laptops</a>'
            '<a href="c/audio/index.html">Audio</a></p></div>\n')
    page("search-no-results.html", "Search: quantum toaster", body)


# --- cart, sign in, sign up --------------------------------------------------------------------------------------
def cart_pages() -> None:
    lines = [(BY_SLUG[s], q) for s, q in DATA["cart"]]
    rows = "".join(
        f'<tr><td><a href="p/{p["slug"]}.html"><img src="img/{p["slug"]}.svg" alt="" width="80" height="60"> {e(p["name"])}</a></td>'
        f'<td>{money(p["price"])}</td>'
        f'<td><form class="qty" action="cart.html" method="get"><input type="hidden" name="line" value="{e(p["slug"])}">'
        f'<button type="submit" name="qty" value="{q - 1}" aria-label="One fewer">−</button>'
        f'<input type="number" name="set" value="{q}" min="1" max="5" aria-label="Quantity of {e(p["name"])}">'
        f'<button type="submit" name="qty" value="{q + 1}" aria-label="One more">+</button></form></td>'
        f'<td>{money(p["price"] * q)}</td>'
        f'<td><a href="cart.html?remove={e(p["slug"])}" class="link-danger">Remove</a></td></tr>' for p, q in lines)
    subtotal = sum(p["price"] * q for p, q in lines)
    body = ('<header class="page-head"><h1>Your cart</h1></header>\n'
            '<div class="cart-layout"><table class="cart-table"><thead><tr><th scope="col">Item</th><th scope="col">Price</th>'
            f'<th scope="col">Quantity</th><th scope="col">Total</th><th scope="col"><span class="sr-only">Remove</span></th></tr></thead><tbody>{rows}</tbody></table>'
            '<aside class="summary" aria-labelledby="sum-h"><h2 id="sum-h">Summary</h2>'
            f'<dl><dt>Subtotal</dt><dd>{money(subtotal)}</dd><dt>Delivery</dt><dd>Free</dd><dt>Total</dt><dd class="total">{money(subtotal)}</dd></dl>'
            '<form action="checkout.html" method="get"><label for="code">Discount code</label>'
            '<input id="code" name="code" type="text"><button type="submit" class="btn btn-ghost">Apply</button></form>'
            '<a class="btn btn-primary wide" href="checkout.html">Checkout</a>'
            '<p class="note"><a href="index.html">Continue shopping</a></p></aside></div>\n')
    page("cart.html", "Your cart", body, signed_in=True)
    body = ('<header class="page-head"><h1>Your cart</h1></header>\n'
            '<div class="empty"><p>Your cart is empty.</p><p><a class="btn btn-primary" href="index.html">Start shopping</a></p>'
            '<p class="note">Signed in? Your cart follows you. <a href="sign-in.html">Sign in</a></p></div>\n')
    page("cart-empty.html", "Your cart is empty", body)
    body = ('<header class="page-head"><h1>Checkout</h1></header>\n'
            '<form class="form" action="checkout.html" method="get">'
            '<fieldset><legend>Delivery address</legend>'
            f'<p><label for="name">Full name</label><input id="name" name="name" value="{e(CUSTOMER["name"])}" required></p>'
            f'<p><label for="street">Street and number</label><input id="street" name="street" value="{e(CUSTOMER["street"])}" required></p>'
            f'<p><label for="city">City</label><input id="city" name="city" value="{e(CUSTOMER["city"])}" required></p>'
            f'<p><label for="zip">Postcode</label><input id="zip" name="zip" value="{e(CUSTOMER["zip"])}" required></p></fieldset>'
            '<fieldset><legend>Payment</legend><label><input type="radio" name="pay" value="card" checked> Card</label>'
            '<label><input type="radio" name="pay" value="paypal"> PayPal</label><label><input type="radio" name="pay" value="invoice"> Invoice</label></fieldset>'
            f'<p class="big">Total {money(subtotal)}</p>'
            '<button type="submit" class="btn btn-primary">Place order</button> <a href="cart.html">Back to cart</a></form>\n')
    page("checkout.html", "Checkout", body, signed_in=True)


def sign_pages() -> None:
    def sign_in(error: bool) -> str:
        banner = '<p class="banner error" role="alert">The email or the password is wrong.</p>' if error else ""
        invalid = ' aria-invalid="true" class="is-invalid"' if error else ""
        return ('<div class="narrow"><header class="page-head"><h1>Sign in</h1></header>' + banner +
                '<form class="form" action="account/profile.html" method="get">'
                f'<p><label for="email">Email</label><input id="email" name="email" type="email" autocomplete="email" required{invalid}'
                + (' value="ana@example.com"' if error else "") + '></p>'
                f'<p><label for="password">Password</label><input id="password" name="password" type="password" autocomplete="current-password" required{invalid}></p>'
                '<p><label><input type="checkbox" name="keep" value="1"> Keep me signed in</label></p>'
                '<button type="submit" class="btn btn-primary wide">Sign in</button>'
                '<p class="note"><a href="forgot-password.html">Forgot your password?</a></p>'
                '<p class="note">New here? <a href="sign-up.html">Create an account</a></p></form></div>\n')
    page("sign-in.html", "Sign in", sign_in(False))
    page("sign-in-refused.html", "Sign in", sign_in(True))

    def sign_up(errors: bool) -> str:
        def field(id_: str, label: str, type_: str, auto: str, msg: str = "", value: str = "") -> str:
            bad = errors and msg
            return (f'<p><label for="{id_}">{label}</label><input id="{id_}" name="{id_}" type="{type_}" autocomplete="{auto}" required'
                    + (f' value="{e(value)}"' if value else "") + (f' aria-invalid="true" class="is-invalid" aria-describedby="{id_}-msg"' if bad else "")
                    + ">" + (f'<span class="msg" id="{id_}-msg">{msg}</span>' if bad else "") + "</p>")
        banner = '<p class="banner error" role="alert">Three things need a look.</p>' if errors else ""
        return ('<div class="narrow"><header class="page-head"><h1>Create an account</h1></header>' + banner +
                '<form class="form" action="sign-up-errors.html" method="get">'
                + field("name", "Full name", "text", "name", "", "Ana" if errors else "")
                + field("email", "Email", "email", "email", "That is not an email address.", "ana@" if errors else "")
                + field("password", "Password", "password", "new-password", "At least 8 characters, with a number.")
                + field("confirm", "Repeat the password", "password", "new-password", "The two passwords differ.")
                + '<p><label><input type="checkbox" name="terms" value="1" required> I accept the <a href="terms.html">terms</a></label></p>'
                '<button type="submit" class="btn btn-primary wide">Create account</button>'
                '<p class="note">Already have one? <a href="sign-in.html">Sign in</a></p></form></div>\n')
    page("sign-up.html", "Create an account", sign_up(False))
    page("sign-up-errors.html", "Create an account", sign_up(True))
    page("forgot-password.html", "Forgot your password",
         '<div class="narrow"><header class="page-head"><h1>Forgot your password?</h1>'
         '<p class="lead">Tell us your email and we send a link to choose a new one.</p></header>'
         '<form class="form" action="forgot-password-sent.html" method="get">'
         '<p><label for="email">Email</label><input id="email" name="email" type="email" required></p>'
         '<button type="submit" class="btn btn-primary wide">Send the link</button></form></div>\n')
    page("forgot-password-sent.html", "Check your email",
         '<div class="narrow"><header class="page-head"><h1>Check your email</h1>'
         '<p class="lead">If an account has that address, a link is on its way. It works for one hour.</p></header>'
         '<p><a href="sign-in.html">Back to sign in</a></p></div>\n')
    page("signed-out.html", "Signed out",
         '<div class="narrow"><header class="page-head"><h1>You are signed out</h1>'
         '<p class="lead">Your cart is kept for the next time you sign in.</p></header>'
         '<p><a class="btn btn-primary" href="index.html">Back to the shop</a> <a href="sign-in.html">Sign in again</a></p></div>\n')


# --- the account, the admin --------------------------------------------------------------------------------------
def status_badge(status: str) -> str:
    return f'<span class="status {status}">{STATUS_WORDS[status]}</span>'


def order_total(o: dict) -> float:
    return sum(BY_SLUG[s]["price"] * q for s, q in o["lines"])


def account_nav(up: str, current: str) -> str:
    links = [("profile", "Profile", f"{up}account/profile.html"), ("orders", "My orders", f"{up}account/orders.html"),
             ("admin", "Admin · orders", f"{up}admin/orders.html"), ("out", "Sign out", f"{up}signed-out.html")]
    return ('<nav class="side-nav" aria-label="Your account"><ul>' +
            "".join(f'<li><a href="{href}"{" aria-current=\"page\"" if key == current else ""}>{label}</a></li>' for key, label, href in links)
            + "</ul></nav>")


def order_lines(o: dict, up: str) -> str:
    rows = "".join(f'<tr><td><a href="{up}p/{BY_SLUG[s]["slug"]}.html">{e(BY_SLUG[s]["name"])}</a></td><td>{q}</td>'
                   f'<td>{money(BY_SLUG[s]["price"] * q)}</td></tr>' for s, q in o["lines"])
    return ('<table class="lines"><thead><tr><th scope="col">Item</th><th scope="col">Qty</th><th scope="col">Total</th></tr></thead>'
            f'<tbody>{rows}</tbody><tfoot><tr><th scope="row" colspan="2">Total</th><td>{money(order_total(o))}</td></tr></tfoot></table>')


def timeline(o: dict) -> str:
    if o["status"] == "cancelled":
        return '<ol class="timeline"><li class="done">Placed</li><li class="stop">Cancelled</li></ol>'
    reached = STATUS_ORDER.index(o["status"])
    return '<ol class="timeline">' + "".join(
        f'<li class="{"done" if i <= reached else ""}"{" aria-current=\"step\"" if i == reached else ""}>{STATUS_WORDS[s]}</li>'
        for i, s in enumerate(STATUS_ORDER)) + "</ol>"


def account_pages() -> None:
    up = "../"
    body = ('<div class="account"><header class="page-head"><h1>My account</h1></header>' + account_nav(up, "profile") +
            '<section aria-labelledby="profile-h"><h2 id="profile-h">Profile</h2>'
            '<form class="form" action="profile.html" method="get">'
            f'<p><label for="name">Full name</label><input id="name" name="name" value="{e(CUSTOMER["name"])}"></p>'
            f'<p><label for="email">Email</label><input id="email" name="email" type="email" value="{e(CUSTOMER["email"])}"></p>'
            f'<p><label for="phone">Phone</label><input id="phone" name="phone" type="tel" value="{e(CUSTOMER["phone"])}"></p>'
            '<fieldset><legend>Delivery address</legend>'
            f'<p><label for="street">Street and number</label><input id="street" name="street" value="{e(CUSTOMER["street"])}"></p>'
            f'<p><label for="city">City</label><input id="city" name="city" value="{e(CUSTOMER["city"])}"></p>'
            f'<p><label for="zip">Postcode</label><input id="zip" name="zip" value="{e(CUSTOMER["zip"])}"></p></fieldset>'
            '<button type="submit" class="btn btn-primary">Save changes</button></form>'
            '<h2>Password</h2><form class="form" action="profile.html" method="get">'
            '<p><label for="current">Current password</label><input id="current" name="current" type="password" autocomplete="current-password"></p>'
            '<p><label for="new">New password</label><input id="new" name="new" type="password" autocomplete="new-password"></p>'
            '<button type="submit" class="btn btn-ghost">Change the password</button></form>'
            '<h2>Danger zone</h2><p><a class="link-danger" href="profile.html#delete">Delete my account</a></p></section></div>\n')
    page("account/profile.html", "Profile", body, signed_in=True)
    mine = [o for o in ORDERS if o["customer"] == CUSTOMER["email"]]
    rows = "".join(f'<tr><td><a href="orders/{o["number"]}.html">{o["number"]}</a></td><td>{o["date"]}</td>'
                   f'<td>{len(o["lines"])}</td><td>{money(order_total(o))}</td><td>{status_badge(o["status"])}</td></tr>' for o in mine)
    body = ('<div class="account"><header class="page-head"><h1>My account</h1></header>' + account_nav(up, "orders") +
            '<section aria-labelledby="orders-h"><h2 id="orders-h">My orders</h2>'
            '<table class="orders"><thead><tr><th scope="col">Order</th><th scope="col">Date</th><th scope="col">Items</th>'
            f'<th scope="col">Total</th><th scope="col">Status</th></tr></thead><tbody>{rows}</tbody></table></section></div>\n')
    page("account/orders.html", "My orders", body, signed_in=True)
    for o in mine:
        up2 = "../../"
        actions = ('<form action="../orders.html" method="get"><input type="hidden" name="cancel" value="' + e(o["number"]) + '">'
                   '<button type="submit" class="btn btn-ghost">Cancel this order</button></form>'
                   if o["status"] in ("placed", "paid") else "")
        body = ('<div class="account"><header class="page-head"><h1>My account</h1></header>' + account_nav(up2, "orders") +
                f'<section aria-labelledby="o-h"><p class="crumb-line"><a href="../orders.html">My orders</a> › {o["number"]}</p>'
                f'<h2 id="o-h">Order {o["number"]} {status_badge(o["status"])}</h2><p class="meta">Placed on {o["date"]}</p>'
                + timeline(o) + order_lines(o, up2) +
                f'<h3>Delivery</h3><p>{e(CUSTOMER["name"])}<br>{e(CUSTOMER["street"])}<br>{e(CUSTOMER["zip"])} {e(CUSTOMER["city"])}</p>'
                + actions + "</section></div>\n")
        page(f"account/orders/{o['number']}.html", f"Order {o['number']}", body, signed_in=True)


def admin_pages() -> None:
    up = "../"
    views = [("orders.html", "All", lambda o: True), ("orders-open.html", "Open", lambda o: o["status"] in ("placed", "paid")),
             ("orders-shipped.html", "Shipped", lambda o: o["status"] in ("shipped", "delivered")),
             ("orders-cancelled.html", "Cancelled", lambda o: o["status"] == "cancelled")]
    for file, label, keep in views:
        shown = [o for o in ORDERS if keep(o)]
        chips = "".join(f'<a href="{f}"{" aria-current=\"page\"" if f == file else ""}>{l} ({len([o for o in ORDERS if k(o)])})</a>'
                        for f, l, k in views)
        rows = "".join(f'<tr><td><a href="orders/{o["number"]}.html">{o["number"]}</a></td><td>{o["date"]}</td><td>{e(o["customer"])}</td>'
                       f'<td>{len(o["lines"])}</td><td>{money(order_total(o))}</td><td>{status_badge(o["status"])}</td></tr>' for o in shown)
        body = ('<div class="account"><header class="page-head"><h1>Admin</h1></header>' + account_nav(up, "admin") +
                f'<section aria-labelledby="admin-h"><h2 id="admin-h">Orders</h2><p class="chips filters">{chips}</p>'
                '<form class="find" action="orders.html" method="get"><label for="find">Find an order</label>'
                '<input id="find" name="q" placeholder="Number or customer email"><button type="submit" class="btn btn-ghost">Find</button></form>'
                '<table class="orders"><thead><tr><th scope="col">Order</th><th scope="col">Date</th><th scope="col">Customer</th>'
                f'<th scope="col">Items</th><th scope="col">Total</th><th scope="col">Status</th></tr></thead><tbody>{rows}</tbody></table>'
                + ("" if shown else "<p class=\"empty\">No orders here.</p>") + "</section></div>\n")
        page(f"admin/{file}", f"Admin · {label} orders", body, signed_in=True)
    for o in ORDERS:
        up2 = "../../"
        nexts = {"placed": [("paid", "Mark as paid"), ("cancelled", "Cancel the order")],
                 "paid": [("shipped", "Mark as shipped"), ("cancelled", "Cancel the order")],
                 "shipped": [("delivered", "Mark as delivered")], "delivered": [], "cancelled": []}[o["status"]]
        actions = "".join(f'<form action="{o["number"]}.html" method="get"><input type="hidden" name="status" value="{s}">'
                          f'<button type="submit" class="btn {"btn-primary" if s != "cancelled" else "btn-danger"}">{label}</button></form>'
                          for s, label in nexts) or "<p class=\"note\">Nothing more to do with this order.</p>"
        body = ('<div class="account"><header class="page-head"><h1>Admin</h1></header>' + account_nav(up2, "admin") +
                f'<section aria-labelledby="o-h"><p class="crumb-line"><a href="../orders.html">Orders</a> › {o["number"]}</p>'
                f'<h2 id="o-h">Order {o["number"]} {status_badge(o["status"])}</h2>'
                f'<p class="meta">Placed on {o["date"]} by <a href="mailto:{e(o["customer"])}">{e(o["customer"])}</a></p>'
                + timeline(o) + order_lines(o, up2) + f'<h3>Actions</h3><div class="actions">{actions}</div>'
                '<h3>Notes</h3><form class="form" action="' + o["number"] + '.html" method="get"><label for="note">Add a note</label>'
                '<textarea id="note" name="note" rows="3"></textarea><button type="submit" class="btn btn-ghost">Add</button></form>'
                "</section></div>\n")
        page(f"admin/orders/{o['number']}.html", f"Admin · order {o['number']}", body, signed_in=True)
    page("admin/forbidden.html", "Not allowed",
         '<div class="narrow"><header class="page-head"><h1>Not allowed</h1>'
         '<p class="lead">This part of the shop is for its staff. You are signed in as a customer.</p></header>'
         '<p><a class="btn btn-primary" href="../index.html">Back to the shop</a></p></div>\n', signed_in=True)


def plain_pages() -> None:
    page("about.html", "About", '<div class="narrow"><header class="page-head"><h1>About Voltline</h1>'
         '<p class="lead">A small electronics shop, since 2019, run from a warehouse in Leipzig.</p></header>'
         '<p>We pick a few products in each category and know them well. Every order leaves the same day it is paid before 15:00.</p></div>\n')
    page("contact.html", "Contact", '<div class="narrow"><header class="page-head"><h1>Contact</h1></header>'
         '<form class="form" action="contact.html" method="get"><p><label for="email">Your email</label><input id="email" name="email" type="email" required></p>'
         '<p><label for="order">Order number, if it is about one</label><input id="order" name="order"></p>'
         '<p><label for="message">Message</label><textarea id="message" name="message" rows="5" required></textarea></p>'
         '<button type="submit" class="btn btn-primary">Send</button></form>'
         '<p class="note">Or call +49 341 000 000, Monday to Friday, 9 to 17.</p></div>\n')
    page("terms.html", "Terms", '<div class="narrow"><header class="page-head"><h1>Terms of sale</h1></header>'
         '<h2>Prices</h2><p>Prices include VAT. A price shown as a deal holds until the stock shown at that price is sold.</p>'
         '<h2>Orders</h2><p>An order is placed when it is confirmed, paid when the payment clears, and may be cancelled by the customer until it is shipped.</p>'
         '<h2>Returns</h2><p>Thirty days from delivery, unused and in its box. The refund goes the way the payment came.</p></div>\n')
    page("shipping.html", "Shipping and returns", '<div class="narrow"><header class="page-head"><h1>Shipping &amp; returns</h1></header>'
         '<p>Free delivery over €50, €4.90 under. Two working days in Germany, four in the rest of the EU.</p>'
         '<p>To return something, open the order under My orders and press Return; a label is emailed within a day.</p></div>\n')


# --- the pictures -------------------------------------------------------------------------------------------------
def svg(body: str, bg: str = "#f3f4f6") -> str:
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="400" height="300" role="img">'
            f'<rect width="400" height="300" rx="16" fill="{bg}"/>'
            '<ellipse cx="200" cy="262" rx="120" ry="12" fill="#000" opacity="0.08"/>' + body + "</svg>\n")


def draw(kind: str, a: str, b: str) -> str:
    """One flat drawing per kind of product, in the product's two colours: the body, and a light."""
    if kind == "laptop":
        return svg(f'<rect x="90" y="60" width="220" height="150" rx="10" fill="{a}"/><rect x="104" y="72" width="192" height="122" rx="4" fill="#111827"/>'
                   f'<rect x="120" y="86" width="90" height="10" rx="5" fill="{b}" opacity="0.9"/><rect x="120" y="104" width="150" height="6" rx="3" fill="#374151"/>'
                   '<rect x="120" y="118" width="120" height="6" rx="3" fill="#374151"/>'
                   f'<path d="M60 214h280l14 22a6 6 0 0 1-5 9H51a6 6 0 0 1-5-9z" fill="{a}"/><rect x="170" y="216" width="60" height="6" rx="3" fill="#000" opacity="0.2"/>')
    if kind == "phone":
        return svg(f'<rect x="150" y="30" width="100" height="210" rx="18" fill="{a}"/><rect x="158" y="40" width="84" height="190" rx="12" fill="#111827"/>'
                   f'<rect x="166" y="52" width="68" height="40" rx="6" fill="{b}" opacity="0.9"/><rect x="166" y="100" width="68" height="8" rx="4" fill="#374151"/>'
                   '<rect x="166" y="114" width="48" height="8" rx="4" fill="#374151"/><circle cx="200" cy="222" r="5" fill="#374151"/>'
                   '<rect x="185" y="44" width="30" height="5" rx="2.5" fill="#000"/>')
    if kind == "tablet":
        return svg(f'<rect x="90" y="40" width="220" height="200" rx="16" fill="{a}"/><rect x="104" y="52" width="192" height="176" rx="8" fill="#111827"/>'
                   f'<rect x="116" y="64" width="80" height="60" rx="6" fill="{b}" opacity="0.9"/><rect x="204" y="64" width="80" height="60" rx="6" fill="#374151"/>'
                   '<rect x="116" y="134" width="168" height="8" rx="4" fill="#374151"/><rect x="116" y="150" width="120" height="8" rx="4" fill="#374151"/>')
    if kind == "watch":
        return svg(f'<rect x="170" y="20" width="60" height="70" rx="12" fill="{b}"/><rect x="170" y="210" width="60" height="70" rx="12" fill="{b}"/>'
                   f'<rect x="140" y="80" width="120" height="140" rx="30" fill="{a}"/><rect x="152" y="92" width="96" height="116" rx="22" fill="#111827"/>'
                   f'<circle cx="200" cy="150" r="34" fill="none" stroke="{b}" stroke-width="8"/><path d="M200 150l0-22M200 150l14 10" stroke="#fff" stroke-width="4" stroke-linecap="round"/>'
                   f'<rect x="258" y="130" width="8" height="24" rx="3" fill="{a}"/>')
    if kind == "headphones":
        return svg(f'<path d="M110 170V140a90 90 0 0 1 180 0v30" fill="none" stroke="{a}" stroke-width="18" stroke-linecap="round"/>'
                   f'<rect x="80" y="150" width="56" height="90" rx="20" fill="{a}"/><rect x="264" y="150" width="56" height="90" rx="20" fill="{a}"/>'
                   f'<rect x="96" y="162" width="24" height="66" rx="12" fill="{b}"/><rect x="280" y="162" width="24" height="66" rx="12" fill="{b}"/>')
    if kind == "earbuds":
        return svg(f'<rect x="110" y="110" width="180" height="120" rx="30" fill="{a}"/><rect x="118" y="100" width="164" height="34" rx="14" fill="{b}"/>'
                   '<circle cx="165" cy="175" r="22" fill="#fff"/><circle cx="235" cy="175" r="22" fill="#fff"/>'
                   f'<rect x="156" y="190" width="18" height="34" rx="9" fill="#fff"/><rect x="226" y="190" width="18" height="34" rx="9" fill="#fff"/>'
                   f'<circle cx="200" cy="120" r="5" fill="{a}"/>')
    if kind == "speaker":
        return svg(f'<rect x="110" y="70" width="180" height="170" rx="24" fill="{a}"/><rect x="124" y="84" width="152" height="142" rx="16" fill="#111827" opacity="0.85"/>'
                   f'<circle cx="200" cy="160" r="44" fill="{b}"/><circle cx="200" cy="160" r="20" fill="#111827"/><circle cx="200" cy="108" r="10" fill="{b}"/>'
                   f'<rect x="150" y="54" width="100" height="16" rx="8" fill="{b}"/>')
    if kind == "soundbar":
        return svg(f'<rect x="40" y="150" width="320" height="56" rx="28" fill="{a}"/><rect x="60" y="162" width="280" height="32" rx="16" fill="#111827" opacity="0.8"/>'
                   + "".join(f'<circle cx="{x}" cy="178" r="8" fill="{b}"/>' for x in range(90, 320, 36)) +
                   '<rect x="120" y="80" width="160" height="60" rx="6" fill="#111827"/><rect x="190" y="140" width="20" height="10" fill="#374151"/>')
    if kind == "camera":
        return svg(f'<rect x="70" y="100" width="260" height="140" rx="18" fill="{a}"/><rect x="140" y="76" width="80" height="30" rx="8" fill="{a}"/>'
                   f'<circle cx="220" cy="170" r="54" fill="#111827"/><circle cx="220" cy="170" r="40" fill="{b}"/><circle cx="220" cy="170" r="22" fill="#111827"/>'
                   '<circle cx="232" cy="158" r="6" fill="#fff" opacity="0.7"/><rect x="92" y="122" width="44" height="30" rx="4" fill="#111827"/>'
                   f'<circle cx="300" cy="124" r="8" fill="{b}"/>')
    if kind == "lens":
        return svg(f'<rect x="120" y="60" width="160" height="180" rx="14" fill="{a}"/><rect x="120" y="100" width="160" height="40" fill="#111827"/>'
                   f'<rect x="120" y="170" width="160" height="30" fill="{b}"/><ellipse cx="200" cy="62" rx="70" ry="16" fill="#111827"/>'
                   '<ellipse cx="200" cy="62" rx="48" ry="10" fill="#1f2937"/><ellipse cx="200" cy="62" rx="26" ry="6" fill="#6d28d9" opacity="0.8"/>')
    if kind == "action-cam":
        return svg(f'<rect x="110" y="90" width="180" height="130" rx="20" fill="{a}"/><rect x="124" y="104" width="70" height="70" rx="12" fill="#111827"/>'
                   f'<circle cx="159" cy="139" r="22" fill="{b}"/><circle cx="159" cy="139" r="10" fill="#111827"/>'
                   '<rect x="210" y="112" width="64" height="44" rx="6" fill="#111827"/><rect x="216" y="118" width="52" height="32" rx="3" fill="#60a5fa"/>'
                   f'<rect x="130" y="76" width="40" height="18" rx="6" fill="{b}"/>')
    if kind == "drone":
        return svg(f'<rect x="150" y="130" width="100" height="50" rx="16" fill="{a}"/><circle cx="200" cy="160" r="12" fill="#111827"/>'
                   + "".join(f'<path d="M200 155L{x} {y}" stroke="{a}" stroke-width="10" stroke-linecap="round"/>'
                             f'<ellipse cx="{x}" cy="{y}" rx="44" ry="8" fill="{b}" opacity="0.8"/><circle cx="{x}" cy="{y}" r="6" fill="#111827"/>'
                             for x, y in ((90, 100), (310, 100), (90, 210), (310, 210))))
    if kind == "instant":
        return svg(f'<rect x="90" y="90" width="220" height="150" rx="22" fill="{a}"/><rect x="110" y="110" width="180" height="20" rx="10" fill="{b}"/>'
                   f'<circle cx="200" cy="185" r="40" fill="#111827"/><circle cx="200" cy="185" r="26" fill="{b}"/><circle cx="200" cy="185" r="12" fill="#111827"/>'
                   '<rect x="120" y="150" width="30" height="30" rx="6" fill="#111827"/><rect x="250" y="150" width="30" height="20" rx="4" fill="#fff"/>')
    if kind == "monitor":
        return svg(f'<rect x="60" y="50" width="280" height="170" rx="10" fill="{a}"/><rect x="70" y="60" width="260" height="150" rx="4" fill="#111827"/>'
                   f'<rect x="90" y="80" width="140" height="70" rx="6" fill="{b}" opacity="0.9"/><rect x="240" y="80" width="70" height="30" rx="4" fill="#374151"/>'
                   '<rect x="240" y="118" width="70" height="30" rx="4" fill="#374151"/><rect x="90" y="160" width="220" height="8" rx="4" fill="#374151"/>'
                   f'<rect x="185" y="220" width="30" height="24" fill="{a}"/><rect x="140" y="244" width="120" height="10" rx="5" fill="{a}"/>')
    if kind == "tv":
        return svg(f'<rect x="40" y="40" width="320" height="190" rx="8" fill="{a}"/><rect x="48" y="48" width="304" height="174" rx="3" fill="#111827"/>'
                   f'<path d="M48 222V110c60-30 120-40 200-10s60 60 104 40v82z" fill="{b}" opacity="0.85"/>'
                   f'<rect x="120" y="236" width="160" height="8" rx="4" fill="{a}"/><rect x="190" y="230" width="20" height="8" fill="{a}"/>')
    if kind == "projector":
        return svg(f'<rect x="90" y="110" width="220" height="100" rx="22" fill="{a}"/><circle cx="140" cy="160" r="30" fill="#111827"/><circle cx="140" cy="160" r="18" fill="{b}"/>'
                   '<circle cx="140" cy="160" r="8" fill="#fff" opacity="0.6"/><rect x="200" y="130" width="90" height="12" rx="6" fill="#111827" opacity="0.5"/>'
                   f'<rect x="200" y="152" width="60" height="12" rx="6" fill="#111827" opacity="0.5"/><path d="M110 120L60 60h120z" fill="{b}" opacity="0.25"/>')
    if kind == "keyboard":
        keys = "".join(f'<rect x="{x}" y="{y}" width="22" height="18" rx="4" fill="{b}" opacity="0.95"/>'
                       for y in (118, 144, 170) for x in range(74, 320, 28))
        return svg(f'<rect x="60" y="104" width="280" height="110" rx="14" fill="{a}"/>' + keys +
                   f'<rect x="130" y="196" width="140" height="12" rx="6" fill="{b}" opacity="0.95"/>')
    if kind == "mouse":
        return svg(f'<path d="M140 110a60 60 0 0 1 120 0v80a60 60 0 0 1-120 0z" fill="{a}"/><path d="M200 60v70" stroke="#111827" stroke-width="3"/>'
                   f'<rect x="192" y="88" width="16" height="30" rx="8" fill="{b}"/><path d="M140 130h120" stroke="#111827" stroke-width="3" opacity="0.4"/>')
    if kind == "hub":
        return svg(f'<rect x="80" y="130" width="240" height="60" rx="14" fill="{a}"/>'
                   + "".join(f'<rect x="{x}" y="146" width="30" height="28" rx="4" fill="#111827"/><rect x="{x + 6}" y="156" width="18" height="8" fill="{b}"/>'
                             for x in (96, 140, 184, 228, 272)) +
                   f'<path d="M320 160h30" stroke="{a}" stroke-width="10" stroke-linecap="round"/><rect x="348" y="148" width="20" height="24" rx="4" fill="{b}"/>')
    if kind == "charger":
        return svg(f'<rect x="130" y="90" width="140" height="140" rx="28" fill="{a}"/><rect x="156" y="60" width="14" height="40" rx="4" fill="#9ca3af"/>'
                   f'<rect x="230" y="60" width="14" height="40" rx="4" fill="#9ca3af"/><rect x="160" y="190" width="80" height="20" rx="6" fill="#111827"/>'
                   f'<rect x="172" y="196" width="56" height="8" rx="4" fill="{b}"/><text x="200" y="160" font-family="system-ui, sans-serif" font-size="28" font-weight="700" fill="#fff" text-anchor="middle">65W</text>')
    if kind == "router":
        return svg(f'<rect x="80" y="150" width="240" height="70" rx="16" fill="{a}"/>'
                   + "".join(f'<rect x="{x}" y="60" width="12" height="96" rx="6" fill="#111827"/>' for x in (110, 194, 278)) +
                   "".join(f'<circle cx="{x}" cy="185" r="6" fill="{b}"/>' for x in (110, 134, 158, 182)) +
                   f'<path d="M230 185h60" stroke="{b}" stroke-width="4" stroke-linecap="round" opacity="0.6"/>')
    if kind == "ssd":
        return svg(f'<rect x="110" y="100" width="180" height="110" rx="16" fill="{a}"/><rect x="126" y="116" width="100" height="78" rx="8" fill="#111827" opacity="0.85"/>'
                   f'<text x="176" y="164" font-family="system-ui, sans-serif" font-size="26" font-weight="700" fill="{b}" text-anchor="middle">1TB</text>'
                   f'<rect x="240" y="116" width="34" height="78" rx="6" fill="{b}" opacity="0.5"/><rect x="200" y="200" width="60" height="30" rx="6" fill="#111827"/>')
    if kind == "console":
        return svg(f'<rect x="100" y="70" width="200" height="160" rx="18" fill="{a}"/><rect x="100" y="70" width="200" height="40" rx="18" fill="{b}"/>'
                   '<rect x="100" y="100" width="200" height="10" fill="#111827" opacity="0.2"/><rect x="130" y="130" width="140" height="10" rx="5" fill="#111827" opacity="0.5"/>'
                   f'<circle cx="150" cy="190" r="16" fill="#111827"/><circle cx="250" cy="190" r="16" fill="#111827"/><rect x="190" y="180" width="20" height="20" rx="4" fill="{b}"/>')
    raise SystemExit(f"no drawing for {kind}")


def pictures() -> None:
    (ROOT / "img").mkdir(exist_ok=True)
    for p in PRODUCTS:
        (ROOT / "img" / f"{p['slug']}.svg").write_text(draw(p["kind"], p["colour"], p["light"]), encoding="utf-8", newline="\n")
    (ROOT / "img" / "logo.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32" role="img" aria-label="Voltline">'
        '<rect width="32" height="32" rx="8" fill="#2563eb"/><path d="M18 4L8 18h7l-1 10 10-14h-7z" fill="#fde047"/></svg>\n',
        encoding="utf-8", newline="\n")


def main() -> None:
    for p in PRODUCTS:
        if not re.fullmatch(r"[a-z0-9-]+", p["slug"]):
            raise SystemExit(f"a slug is not a name for a file: {p['slug']}")
    pictures()
    home()
    category_pages()
    product_pages()
    search_pages()
    cart_pages()
    sign_pages()
    account_pages()
    admin_pages()
    plain_pages()
    (ROOT / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8", newline="\n")
    print(f"{ROOT.name}: {len(list(ROOT.rglob('*.html')))} pages, {len(PRODUCTS)} products, {len(ORDERS)} orders")


if __name__ == "__main__":
    main()
