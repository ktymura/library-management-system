from __future__ import annotations

from enum import Enum
from typing import Annotated

from app.utils.jwt import verify_and_decode_token
from fastapi import Depends, Header, HTTPException, status


class Role(str, Enum):
    READER = "READER"
    LIBRARIAN = "LIBRARIAN"
    ADMIN = "ADMIN"


def get_bearer_token(
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    return authorization.split(" ", 1)[1].strip()


def get_current_user_claims(token: str = Depends(get_bearer_token)) -> dict:
    return verify_and_decode_token(token)


def require_role(*allowed: Role):
    def _dep(claims: Annotated[dict, Depends(get_current_user_claims)]) -> dict:
        role = claims.get("role") or claims.get("roles") or claims.get("scope")

        # jeżeli roles to lista/ciąg, spróbujmy sprawdzić członkostwo
        def _has(role_value: str) -> bool:
            if role_value is None:
                return False
            if isinstance(role_value, str):
                items = {x.strip() for x in role_value.replace(",", " ").split()}
            elif isinstance(role_value, (list, tuple, set)):
                items = set(role_value)
            else:
                items = {str(role_value)}
            return any(a.value in items for a in allowed)

        if not _has(role):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return claims

    return _dep


# Skrót do najczęstszej potrzeby:
require_librarian_or_admin = require_role(Role.LIBRARIAN, Role.ADMIN)
