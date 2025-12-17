import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# PATH / ENV


CATALOG_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CATALOG_ROOT))

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

from app.deps import get_db  # noqa: E402
from app.main import app  # noqa: E402

# ENGINE (JEDNA CONNECTION NA CAŁĄ SESJĘ)


engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)


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
    alembic_cfg.set_main_option("script_location", str(CATALOG_ROOT / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", "sqlite+pysqlite:///:memory:")
    alembic_cfg.attributes["connection"] = connection
    command.upgrade(alembic_cfg, "head")


# DB SESSION PER TEST (TRANSAKCJA + SAVEPOINT)


@pytest.fixture()
def db_session(connection):
    # zewnętrzna transakcja (rollback po teście)
    transaction = connection.begin()

    session = Session(bind=connection, future=True)

    # SAVEPOINT – pozwala na commit() w kodzie appki
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
