from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.config import settings
from jose import jwt


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    """Zwraca podpisany JWT z sub=<user_id or email>."""
    exp_minutes = expires_minutes or settings.JWT_EXPIRES_MIN
    expire = datetime.now(timezone.utc) + timedelta(minutes=exp_minutes)
    to_encode: dict[str, Any] = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def decode_token(token: str) -> dict:
    """Zwraca payload (walidację błędów dodamy w kolejnym kroku)."""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
