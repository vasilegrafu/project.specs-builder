"""Who may call: an API key per account, with its scopes."""
from __future__ import annotations

from dataclasses import dataclass

from fastapi import Header, HTTPException

# What a key may do. A key without `shipments:write` may track but not create; `webhooks` is given to
# the integrator's key alone, never to one handed to a shop's front end.
SCOPES = ("shipments:read", "shipments:write", "labels", "webhooks")


@dataclass
class Key:
    account: str
    scopes: tuple[str, ...]
    test: bool = False             # a test key: shipments it makes are never collected, and labels say TEST


# Keys are kept hashed in the accounts database; this table stands in for it in the demo.
KEYS: dict[str, Key] = {
    "pp_test_7f3a9c2e": Key("acme-shop", SCOPES, test=True),
    "pp_test_track_only": Key("acme-shop", ("shipments:read",), test=True),
}


def caller(authorization: str = Header(default="")) -> Key:
    """The key behind `Authorization: Bearer <key>`. A missing or unknown key is 401; the scopes are checked where
    the route needs one."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={"error": "no API key: send Authorization: Bearer <key>"})
    key = KEYS.get(authorization[len("Bearer "):])
    if key is None:
        raise HTTPException(status_code=401, detail={"error": "the API key is not known or has been revoked"})
    return key


def needs(key: Key, scope: str) -> None:
    """403 where the key lacks the scope, and the answer says which."""
    if scope not in key.scopes:
        raise HTTPException(status_code=403, detail={"error": f"the key lacks the scope {scope}"})
