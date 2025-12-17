import os
from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.config import settings
from jose import jwt
from passlib.context import CryptContext

# --- hasla ---
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _jwt_runtime_config() -> dict[str, Any]:
    """Allow runtime env overrides (tests monkeypatch JWT_* values)."""
    alg = os.getenv("JWT_ALG", settings.JWT_ALG)
    iss = os.getenv("JWT_ISSUER", settings.JWT_ISSUER)
    aud = os.getenv("JWT_AUDIENCE", settings.JWT_AUDIENCE)
    secret = os.getenv("JWT_SECRET", settings.JWT_SECRET)
    exp_raw = os.getenv("JWT_EXPIRES_MIN")
    exp_minutes = int(exp_raw) if exp_raw is not None else settings.JWT_EXPIRES_MIN
    return {
        "alg": alg,
        "iss": iss,
        "aud": aud,
        "secret": secret,
        "exp_minutes": exp_minutes,
    }


# --- JWT ---
def create_access_token(
    subject: str,
    *,
    role: str | None = None,
    extra: dict[str, Any] | None = None,
    expires_minutes: int | None = None,
) -> str:
    cfg = _jwt_runtime_config()
    exp_minutes = expires_minutes or cfg["exp_minutes"]
    expire = datetime.now(timezone.utc) + timedelta(minutes=exp_minutes)

    payload: dict[str, Any] = {
        "sub": subject,
        "exp": int(expire.timestamp()),  # numeric exp is safest
    }
    if role:
        payload["role"] = role
    if cfg["iss"]:
        payload["iss"] = cfg["iss"]
    if cfg["aud"]:
        payload["aud"] = cfg["aud"]
    if extra:
        payload.update(extra)

    return jwt.encode(payload, cfg["secret"], algorithm=cfg["alg"])


def decode_token(token: str) -> dict[str, Any]:
    cfg = _jwt_runtime_config()
    # verify iss/aud only when provided
    options = {"verify_aud": bool(cfg["aud"])}
    return jwt.decode(
        token,
        cfg["secret"],
        algorithms=[cfg["alg"]],
        issuer=(cfg["iss"] or None),
        audience=(cfg["aud"] or None),
        options=options,
    )
