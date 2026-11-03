"""Customers and their accounts. Owned by the accounts team."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Account:
    id: str
    email: str
    name: str
    is_admin: bool = False
