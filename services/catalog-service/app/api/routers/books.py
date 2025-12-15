from __future__ import annotations

from typing import Annotated

from app.api.security import require_librarian_or_admin
from app.deps import get_db
from app.repositories import BookRepository
from app.schemas import BookCreate, BookRead, BookUpdate
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/books", tags=["Books"])


@router.post(
    "", response_model=BookRead, status_code=201, dependencies=[Depends(require_librarian_or_admin)]
)
def create_book(payload: BookCreate, db: Annotated[Session, Depends(get_db)]):
    repo = BookRepository(db)
    b = repo.create(
        title=payload.title,
        author_id=payload.author_id,
        isbn=payload.isbn,
        published_year=payload.published_year,
    )
    db.commit()
    db.refresh(b)
    return b


@router.get("", response_model=list[BookRead])
def list_books(
    db: Annotated[Session, Depends(get_db)],
    title: str | None = None,
    isbn: str | None = None,
    author_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
):
    repo = BookRepository(db)
    return repo.list(title=title, isbn=isbn, author_id=author_id, limit=limit, offset=offset)


@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int, db: Annotated[Session, Depends(get_db)]):
    repo = BookRepository(db)
    return repo.require(book_id)


@router.patch(
    "/{book_id}", response_model=BookRead, dependencies=[Depends(require_librarian_or_admin)]
)
def update_book(book_id: int, payload: BookUpdate, db: Annotated[Session, Depends(get_db)]):
    repo = BookRepository(db)
    b = repo.update_partial(
        book_id,
        title=payload.title,
        author_id=payload.author_id,
        isbn=payload.isbn,
        published_year=payload.published_year,
    )
    db.commit()
    db.refresh(b)
    return b


@router.delete("/{book_id}", status_code=204, dependencies=[Depends(require_librarian_or_admin)])
def delete_book(book_id: int, db: Annotated[Session, Depends(get_db)]):
    repo = BookRepository(db)
    repo.delete(book_id)
    db.commit()
    return None
