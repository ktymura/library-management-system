from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import AlreadyExists, NotFound
from app.models import Copy, CopyStatus
from app.repositories.books import BookRepository


class CopyRepository:
    def __init__(self, db: Session):
        self.db = db
        self._books = BookRepository(db)

    # CREATE
    def create(
        self, *, book_id: int, inventory_code: str, status: CopyStatus | None = None
    ) -> Copy:
        # upewnij się, że książka istnieje
        self._books.require(book_id)

        copy = Copy(
            book_id=book_id,
            inventory_code=inventory_code,
            status=status or CopyStatus.AVAILABLE,
        )
        self.db.add(copy)
        try:
            self.db.flush()
        except IntegrityError as exc:
            self.db.rollback()
            raise AlreadyExists("Copy with this inventory_code already exists") from exc
        return copy

    # READ
    def list_by_book(self, book_id: int, *, limit: int = 100, offset: int = 0) -> Sequence[Copy]:
        # jeśli książka nie istnieje, rzuć 404 (czytelny błąd)
        self._books.require(book_id)
        stmt = (
            select(Copy)
            .where(Copy.book_id == book_id)
            .order_by(Copy.id)
            .limit(limit)
            .offset(offset)
        )
        return self.db.execute(stmt).scalars().all()

    def get(self, copy_id: int) -> Copy | None:
        return self.db.get(Copy, copy_id)

    def require(self, copy_id: int) -> Copy:
        obj = self.get(copy_id)
        if not obj:
            raise NotFound(f"Copy {copy_id} not found")
        return obj

    # UPDATE (np. status)
    def update_status(self, copy_id: int, *, status: CopyStatus) -> Copy:
        c = self.require(copy_id)
        c.status = status
        self.db.flush()
        return c

    # DELETE
    def delete(self, copy_id: int) -> None:
        c = self.require(copy_id)
        self.db.delete(c)
