"""seed initial admin

Revision ID: fd1143b9b33c
Revises: 521e1975293c
Create Date: 2025-12-16 00:02:49.185239

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
import os

# Revision identifiers, used by Alembic.
revision = "fd1143b9b33c"
down_revision = "521e1975293c"
branch_labels = None
depends_on = None


def _get_env(key: str, default: str | None = None) -> str:
    val = os.environ.get(key, default)
    if not val:
        raise RuntimeError(
            f"Missing required environment variable: {key}. "
            "Set it in your environment or .env file before running migrations."
        )
    return val


def _hash_password(plain: str) -> str:
    """
    Hashujemy lokalnie, bez importowania kodu aplikacji (żeby unikać zależności na Settings).
    Używamy passlib[bcrypt], tak jak zwykle w FastAPI-projektach.
    """
    try:
        from passlib.context import CryptContext
    except Exception as exc:
        raise RuntimeError(
            "passlib is required to hash the admin password in migration. "
            "Add `passlib[bcrypt]` to requirements and reinstall."
        ) from exc

    pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")
    return pwd_context.hash(plain)


def upgrade() -> None:
    bind = op.get_bind()

    admin_email = _get_env("ADMIN_EMAIL", "admin@email.com")
    admin_password_plain = _get_env("ADMIN_PASSWORD", "Admin123!")
    admin_password_hash = _hash_password(admin_password_plain)

    # Sprawdź, czy jakiś ADMIN już istnieje (idempotencja migracji)
    exists = bind.execute(
        text("SELECT 1 FROM users WHERE role = :role LIMIT 1"),
        {"role": "ADMIN"},
    ).fetchone()

    if exists:
        # Nic nie robimy, admin już jest
        return

    # Wstaw predefiniowanego admina
    # created_at/updated_at wypełnią się server_default (jeśli ustawione w schemacie)
    bind.execute(
        text(
            """
            INSERT INTO users (email, hashed_password, role, is_active)
            VALUES (:email, :hashed_password, :role, :is_active)
            """
        ),
        {
            "email": admin_email,
            "hashed_password": admin_password_hash,
            "role": "ADMIN",
            "is_active": True,
        },
    )


def downgrade() -> None:
    bind = op.get_bind()
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@email.com")
    # Usuwamy TYLKO admina o tym konkretnym emailu, żeby nie skasować innych adminów
    bind.execute(
        text("DELETE FROM users WHERE email = :email AND role = :role"),
        {"email": admin_email, "role": "ADMIN"},
    )
