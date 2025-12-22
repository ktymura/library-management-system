from __future__ import annotations

from sqlalchemy.orm import Session

from app.seed.constants import DEMO_COPIES


def seed_demo_copies(db: Session, *, book_ids: dict[str, int]) -> dict[str, int]:
    """
    Seed egzemplarzy:
    - idempotentnie po inventory_code (unikat w DB)
    """
    from app.models.copy import Copy, CopyStatus

    created = 0
    skipped = 0

    existing_codes = {c.inventory_code for c in db.query(Copy.inventory_code).all()}

    for c in DEMO_COPIES:
        if c.inventory_code in existing_codes:
            skipped += 1
            continue

        if c.book_key not in book_ids:
            raise ValueError(f"Book key not found for demo copy: {c.book_key}")

        status = CopyStatus(c.status)  # "AVAILABLE" -> enum
        db.add(
            Copy(
                inventory_code=c.inventory_code,
                book_id=book_ids[c.book_key],
                status=status,
            )
        )
        created += 1

    db.commit()
    return {"created": created, "skipped": skipped}
