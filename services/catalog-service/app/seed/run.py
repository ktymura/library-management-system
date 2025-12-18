from __future__ import annotations

import os


def _is_seed_allowed() -> bool:
    app_env = os.getenv("APP_ENV", "").lower()
    seed_flag = os.getenv("SEED_DATA", "").lower() in {"1", "true", "yes", "y", "on"}
    return seed_flag or app_env in {"demo", "dev", "development"}


def main() -> int:
    if not _is_seed_allowed():
        print("Seed disabled. Set APP_ENV=demo (or dev) or SEED_DATA=true.")
        return 2

    from app.db import SessionLocal
    from app.seed.authors import get_author_id_map, seed_demo_authors
    from app.seed.books import seed_demo_books
    from app.seed.copies import seed_demo_copies

    with SessionLocal() as db:
        a_res = seed_demo_authors(db)
        author_ids = get_author_id_map(db)
        book_ids = seed_demo_books(db, author_ids=author_ids)
        c_res = seed_demo_copies(db, book_ids=book_ids)

    print(f"Seed demo catalog done. Authors: {a_res}, Copies: {c_res}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
