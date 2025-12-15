from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.config import settings
from jose import jwt
from passlib.context import CryptContext

# --- hasła ---
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# --- JWT ---
def create_access_token(
    subject: str,
    *,
    role: str | None = None,
    extra: dict[str, Any] | None = None,
    expires_minutes: int | None = None,
) -> str:
    exp_minutes = expires_minutes or settings.JWT_EXPIRES_MIN
    expire = datetime.now(timezone.utc) + timedelta(minutes=exp_minutes)

    payload: dict[str, Any] = {
        "sub": subject,
        "exp": int(expire.timestamp()),  # numeric exp jest najbezpieczniejszy
    }
    if role:
        payload["role"] = role
    if settings.JWT_ISSUER:
        payload["iss"] = settings.JWT_ISSUER
    if settings.JWT_AUDIENCE:
        payload["aud"] = settings.JWT_AUDIENCE
    if extra:
        payload.update(extra)

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def decode_token(token: str) -> dict[str, Any]:
    # weryfikuj iss/aud tylko jeśli są ustawione
    options = {"verify_aud": bool(settings.JWT_AUDIENCE)}
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALG],
        issuer=(settings.JWT_ISSUER or None),
        audience=(settings.JWT_AUDIENCE or None),
        options=options,
    )
