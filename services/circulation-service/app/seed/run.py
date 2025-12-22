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
    from app.seed.loans import seed_demo_loans

    with SessionLocal() as db:
        res = seed_demo_loans(db)

    print(f"Seed demo loans done: created={res['created']} skipped={res['skipped']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
