from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import AlreadyExists, NotFound
from app.models import Author, Book
from app.repositories.authors import AuthorRepository


class BookRepository:
    def __init__(self, db: Session):
        self.db = db
        self._authors = AuthorRepository(db)

    # CREATE
    def create(
        self, *, title: str, author_id: int, isbn: str | None, published_year: int | None
    ) -> Book:
        # upewnij się, że autor istnieje
        self._authors.require(author_id)

        book = Book(
            title=title,
            author_id=author_id,
            isbn=isbn,
            published_year=published_year,
        )
        self.db.add(book)
        try:
            self.db.flush()  # może rzucić IntegrityError na unikalnym ISBN
        except IntegrityError as exc:
            self.db.rollback()
            raise AlreadyExists("Book with this ISBN already exists") from exc
        return book

    # READ
    def get(self, book_id: int) -> Book | None:
        return self.db.get(Book, book_id)

    def require(self, book_id: int) -> Book:
        obj = self.get(book_id)
        if not obj:
            raise NotFound(f"Book {book_id} not found")
        return obj

    def list(
        self,
        *,
        title: str | None = None,
        isbn: str | None = None,
        author_id: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Book]:
        stmt = select(Book)
        if title:
            stmt = stmt.where(Book.title.ilike(f"%{title}%"))
        if isbn:
            stmt = stmt.where(Book.isbn == isbn)
        if author_id:
            stmt = stmt.where(Book.author_id == author_id)
        stmt = stmt.order_by(Book.id).limit(limit).offset(offset)
        return self.db.execute(stmt).scalars().all()

    def search(
        self,
        *,
        query: str,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Book]:
        q = query.strip()

        stmt = (
            select(Book)
            .join(Author, Book.author_id == Author.id)
            .where(
                or_(
                    Book.title.ilike(f"%{q}%"),
                    Author.full_name.ilike(f"%{q}%"),
                )
            )
            .distinct()
            .order_by(Book.id)
            .limit(limit)
            .offset(offset)
        )
        return self.db.execute(stmt).scalars().all()

    # UPDATE (partial)
    def update_partial(
        self,
        book_id: int,
        *,
        title: str | None = None,
        author_id: int | None = None,
        isbn: str | None = None,
        published_year: int | None = None,
    ) -> Book:
        book = self.require(book_id)

        if author_id is not None:
            self._authors.require(author_id)
            book.author_id = author_id
        if title is not None:
            book.title = title
        if isbn is not None:
            book.isbn = isbn
        if published_year is not None:
            book.published_year = published_year

        try:
            self.db.flush()
        except IntegrityError as exc:
            self.db.rollback()
            raise AlreadyExists("Book with this ISBN already exists") from exc
        return book

    # DELETE
    def delete(self, book_id: int) -> None:
        book = self.require(book_id)
        self.db.delete(book)
        # flush/commit po stronie warstwy wyższej
