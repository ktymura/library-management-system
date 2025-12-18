from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DemoUser:
    email: str
    password: str
    full_name: str
    role: str


DEMO_USERS: list[DemoUser] = [
    DemoUser(
        email="reader@demo.com", password="Demo1234!#", full_name="Demo Reader", role="READER"
    ),
    DemoUser(
        email="librarian@demo.com",
        password="Demo1234!#",
        full_name="Demo Librarian",
        role="LIBRARIAN",
    ),
]
