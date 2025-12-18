import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

# PATH / ENV
CIRCULATION_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CIRCULATION_ROOT))

from app.core.config import settings  # noqa: E402
from app.deps import get_db  # noqa: E402
from app.main import app  # noqa: E402

# SQLite in-memory wymaga StaticPool + check_same_thread
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
# Postgres i reszta: zwykły engine
else:
    engine = create_engine(settings.DATABASE_URL, future=True)


# CONNECTION (SESSION SCOPE)


@pytest.fixture(scope="session")
def connection():
    conn = engine.connect()
    yield conn
    conn.close()


# ALEMBIC UPGRADE HEAD (RAZ NA SESJĘ)


@pytest.fixture(scope="session", autouse=True)
def apply_migrations(connection):
    from alembic.config import Config, command

    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", str(CIRCULATION_ROOT / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    alembic_cfg.attributes["connection"] = connection
    command.upgrade(alembic_cfg, "head")


# DB SESSION PER TEST (TRANSAKCJA + SAVEPOINT)


@pytest.fixture()
def db_session(connection):
    transaction = connection.begin()
    session = Session(bind=connection, future=True)

    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()


# OVERRIDE FastAPI get_db


@pytest.fixture(autouse=True)
def override_get_db(db_session):
    def _get_db_override():
        yield db_session

    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()


# TEST CLIENT


@pytest.fixture()
def client():
    return TestClient(app)
