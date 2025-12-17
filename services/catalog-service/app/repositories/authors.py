from __future__ import annotations

from collections.abc import Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import AlreadyExists, NotFound
from app.models import Author


class AuthorRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, full_name: str) -> Author:
        author = Author(full_name=full_name)
        self.db.add(author)
        self.db.flush()  # uzyskaj id bez commit
        return author

    def get(self, author_id: int) -> Author | None:
        return self.db.get(Author, author_id)

    def require(self, author_id: int) -> Author:
        obj = self.get(author_id)
        if not obj:
            raise NotFound(f"Author {author_id} not found")
        return obj

    def list(self, *, q: str | None = None, limit: int = 50, offset: int = 0) -> Sequence[Author]:
        stmt = select(Author).order_by(Author.id).limit(limit).offset(offset)
        if q:
            stmt = (
                select(Author)
                .where(Author.full_name.ilike(f"%{q}%"))
                .order_by(Author.id)
                .limit(limit)
                .offset(offset)
            )
        return self.db.execute(stmt).scalars().all()

    def update_partial(
        self,
        author_id: int,
        *,
        full_name: str | None = None,
    ) -> Author:
        author = self.require(author_id)

        if full_name is not None:
            author.full_name = full_name

        try:
            self.db.flush()
        except IntegrityError as exc:
            self.db.rollback()
            raise AlreadyExists("Author with this name already exists") from exc
        return author
