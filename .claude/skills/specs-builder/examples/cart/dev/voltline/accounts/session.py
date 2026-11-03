"""Who is calling: the session cookie, and the account behind it where someone is signed in."""
from __future__ import annotations

import secrets
from dataclasses import dataclass

from fastapi import Cookie, Response

from voltline.cart import service as cart

SESSION_COOKIE = "session"
SESSION_DAYS = 30


@dataclass
class Session:
    id: str
    account_id: str | None = None       # None for a visitor
    is_admin: bool = False


SESSIONS: dict[str, Session] = {}


def current_session(response: Response, session: str | None = Cookie(default=None)) -> Session:
    """The caller's session; a visitor without one gets a new cookie, so that their cart has an owner."""
    if session and session in SESSIONS:
        return SESSIONS[session]
    made = Session(id="s_" + secrets.token_hex(12))
    SESSIONS[made.id] = made
    response.set_cookie(SESSION_COOKIE, made.id, max_age=SESSION_DAYS * 86400, httponly=True, samesite="lax")
    return made


def sign_in(session: Session, account_id: str, is_admin: bool = False) -> Session:
    """The visitor becomes the customer: their cart joins the account's."""
    visitor_cart = cart.cart_for(session.id)
    session.account_id = account_id
    session.is_admin = is_admin
    if visitor_cart.lines:
        cart.merge(visitor_cart, cart.cart_for(account_id))
    return session
