from __future__ import annotations

from typing import Annotated

from app.api.security import require_librarian_or_admin
from app.deps import get_db
from app.repositories import BookRepository
from app.schemas import BookCreate, BookRead, BookUpdate, ErrorResponse
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

RESP_401_403 = {
    401: {"model": ErrorResponse, "description": "Unauthorized (missing/invalid JWT)"},
    403: {"model": ErrorResponse, "description": "Forbidden (insufficient role)"},
}
RESP_404 = {404: {"model": ErrorResponse, "description": "Not found"}}
RESP_409 = {409: {"model": ErrorResponse, "description": "Conflict (already exists)"}}

router = APIRouter(prefix="/books", tags=["Books"])


@router.post(
    "",
    response_model=BookRead,
    status_code=201,
    dependencies=[Depends(require_librarian_or_admin)],
    responses={**RESP_401_403, **RESP_409, **RESP_404},
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


@router.get(
    "",
    response_model=list[BookRead],
    responses={**RESP_404},
)
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


@router.get(
    "/{book_id}", response_model=BookRead, responses={**RESP_401_403, **RESP_404, **RESP_409}
)
def get_book(book_id: int, db: Annotated[Session, Depends(get_db)]):
    repo = BookRepository(db)
    return repo.require(book_id)


@router.patch(
    "/{book_id}",
    response_model=BookRead,
    dependencies=[Depends(require_librarian_or_admin)],
    responses={**RESP_401_403, **RESP_404, **RESP_409},
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


@router.delete(
    "/{book_id}",
    status_code=204,
    dependencies=[Depends(require_librarian_or_admin)],
    responses={**RESP_401_403, **RESP_404, **RESP_409},
)
def delete_book(book_id: int, db: Annotated[Session, Depends(get_db)]):
    repo = BookRepository(db)
    repo.delete(book_id)
    db.commit()
    return None
