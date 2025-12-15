from __future__ import annotations

from app.core.config import settings
from fastapi import HTTPException, status
from jose import JWTError, jwt


class TokenError(HTTPException):
    def __init__(self, detail: str = "Invalid token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


def _get_key_and_alg():
    alg = settings.JWT_ALG
    if alg == "HS256":
        if not settings.JWT_SECRET:
            raise RuntimeError("JWT_SECRET is required for HS256")
        return settings.JWT_SECRET, alg
    if alg == "RS256":
        if not settings.JWT_PUBLIC_KEY:
            raise RuntimeError("JWT_PUBLIC_KEY is required for RS256")
        return settings.JWT_PUBLIC_KEY.replace("\\n", "\n"), alg
    raise RuntimeError(f"Unsupported JWT_ALG: {alg}")


def verify_and_decode_token(token: str) -> dict:
    key, alg = _get_key_and_alg()
    options = {"verify_aud": bool(settings.JWT_AUDIENCE)}
    try:
        claims = jwt.decode(
            token,
            key,
            algorithms=[alg],
            issuer=settings.JWT_ISSUER if settings.JWT_ISSUER else None,
            audience=settings.JWT_AUDIENCE if settings.JWT_AUDIENCE else None,
            options=options,
        )
    except JWTError as e:
        raise TokenError("Invalid or expired token") from e
    return claims
