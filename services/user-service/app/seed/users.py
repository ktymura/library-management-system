from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.seed.constants import DEMO_USERS


def seed_demo_users(db: Session) -> dict[str, int]:
    """
    Idempotentne seedowanie użytkowników demo.
    - jeśli email istnieje -> pomijamy
    - jeśli nie -> tworzymy z zahashowanym hasłem
    Zwraca licznik: created / skipped
    """

    created = 0
    skipped = 0

    for u in DEMO_USERS:
        existing = db.query(User).filter(User.email == u.email).first()
        if existing:
            skipped += 1
            continue

        user = User(
            email=u.email,
            hashed_password=get_password_hash(u.password),
            full_name=u.full_name,
            role=u.role,
            is_active=True,
        )
        db.add(user)
        created += 1

    db.commit()
    return {"created": created, "skipped": skipped}
