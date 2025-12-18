from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings


class Base(DeclarativeBase):
    pass


# SQLite in-memory wymaga StaticPool + check_same_thread
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
# Postgres: zwykły engine
else:
    engine = create_engine(settings.DATABASE_URL, future=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
