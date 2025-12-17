from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class CopyStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    BORROWED = "BORROWED"
    LOST = "LOST"
    DAMAGED = "DAMAGED"


class Copy(Base):
    __tablename__ = "copies"
    __table_args__ = (
        UniqueConstraint("inventory_code", name="uq_copies_inventory_code"),
        Index("ix_copies_book_id", "book_id"),
        Index("ix_copies_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # unikalny kod egzemplarza w bibliotece, np. „BC-2025-000123”
    inventory_code: Mapped[str] = mapped_column(String(64), nullable=False)

    status: Mapped[CopyStatus] = mapped_column(
        SAEnum(CopyStatus, name="copy_status"),
        nullable=False,
        default=CopyStatus.AVAILABLE,
        server_default=CopyStatus.AVAILABLE.value,
    )

    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # relacje
    book: Mapped[Book] = relationship(back_populates="copies")
