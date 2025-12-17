from __future__ import annotations

from enum import Enum
from typing import Annotated

from app.utils.jwt import verify_and_decode_token
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer_scheme = HTTPBearer(auto_error=False)


class Role(str, Enum):
    READER = "READER"
    LIBRARIAN = "LIBRARIAN"
    ADMIN = "ADMIN"


def get_current_user_claims(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> dict:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return verify_and_decode_token(creds.credentials)


def require_role(*allowed: Role):
    def _dep(claims: Annotated[dict, Depends(get_current_user_claims)]) -> dict:
        role = claims.get("role")
        if role not in {a.value for a in allowed}:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return claims

    return _dep


require_librarian_or_admin = require_role(Role.LIBRARIAN, Role.ADMIN)

# Skrót do najczęstszej potrzeby:
require_librarian_or_admin = require_role(Role.LIBRARIAN, Role.ADMIN)
