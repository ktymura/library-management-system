from __future__ import annotations

from enum import Enum

from fastapi import Header, HTTPException, status


class Role(str, Enum):
    READER = "READER"
    LIBRARIAN = "LIBRARIAN"
    ADMIN = "ADMIN"


def require_librarian_or_admin(x_role: str | None = Header(default=None, alias="X-Role")):
    if x_role in (Role.LIBRARIAN, Role.ADMIN):
        return x_role
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
