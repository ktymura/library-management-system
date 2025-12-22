from __future__ import annotations

import os
import sys

from app.seed.users import seed_demo_users


def _is_seed_allowed() -> bool:
    """
    Seed ma działać tylko w demo/dev albo gdy SEED_DATA=true.
    """
    app_env = os.getenv("APP_ENV", "").lower()
    seed_flag = os.getenv("SEED_DATA", "").lower() in {"1", "true", "yes", "y", "on"}
    return seed_flag or app_env in {"demo", "dev", "development"}


def main() -> int:
    if not _is_seed_allowed():
        print("Seed disabled. Set APP_ENV=demo (or dev) or SEED_DATA=true.")
        return 2

    # Importujemy tu, żeby nie ładować DB przy samym imporcie modułu
    from app.db import SessionLocal  # powinno istnieć u Ciebie w app/db.py

    with SessionLocal() as db:
        result = seed_demo_users(db)

    print(f"Seed demo users done: created={result['created']} skipped={result['skipped']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
