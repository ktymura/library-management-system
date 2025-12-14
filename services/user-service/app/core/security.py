from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.config import settings
from jose import jwt
from passlib.context import CryptContext

# --- hasła ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# --- JWT ---
def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    exp_minutes = expires_minutes or settings.JWT_EXPIRES_MIN
    expire = datetime.now(timezone.utc) + timedelta(minutes=exp_minutes)
    to_encode: dict[str, Any] = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
