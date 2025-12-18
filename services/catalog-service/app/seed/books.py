from __future__ import annotations

from sqlalchemy.orm import Session

from app.seed.constants import DEMO_BOOKS


def seed_demo_books(db: Session, *, author_ids: dict[str, int]) -> dict[str, int]:
    """
    Seed książek:
    - idempotentnie po isbn (unikat w DB)
    - zwraca mapę book_key -> book_id
    """
    from app.models.book import Book

    created = 0
    skipped = 0

    # najpierw zbuduj mapę istniejących książek po isbn (żeby nie robić N+1)
    existing_by_isbn = {b.isbn: b for b in db.query(Book).filter(Book.isbn.is_not(None)).all()}

    key_to_id: dict[str, int] = {}

    for b in DEMO_BOOKS:
        if b.author_full_name not in author_ids:
            raise ValueError(f"Author not found for demo book: {b.author_full_name}")

        existing = existing_by_isbn.get(b.isbn)
        if existing:
            skipped += 1
            key_to_id[b.key] = existing.id
            continue

        book = Book(
            title=b.title,
            isbn=b.isbn,
            published_year=b.published_year,
            author_id=author_ids[b.author_full_name],
        )
        db.add(book)
        db.flush()  # żeby dostać book.id bez commit
        created += 1
        key_to_id[b.key] = book.id

    db.commit()
    print(f"Seed demo books: created={created} skipped={skipped}")
    return key_to_id
