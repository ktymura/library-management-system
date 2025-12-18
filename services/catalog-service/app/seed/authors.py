from __future__ import annotations

from sqlalchemy.orm import Session

from app.seed.constants import DEMO_AUTHORS


def seed_demo_authors(db: Session) -> dict[str, int]:
    # lokalne importy = mniej ryzyka cykli
    from app.models.author import Author

    created = 0
    skipped = 0

    for a in DEMO_AUTHORS:
        existing = db.query(Author).filter(Author.full_name == a.full_name).first()
        if existing:
            skipped += 1
            continue

        db.add(Author(full_name=a.full_name))
        created += 1

    db.commit()
    return {"created": created, "skipped": skipped}


def get_author_id_map(db: Session) -> dict[str, int]:
    """Mapuje full_name -> id (do seedowania książek)."""
    from app.models.author import Author

    rows = db.query(Author).all()
    return {r.full_name: r.id for r in rows}
