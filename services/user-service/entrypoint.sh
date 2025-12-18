#!/bin/sh
set -e

# Run migrations on every start so schema is up to date
alembic upgrade head

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
