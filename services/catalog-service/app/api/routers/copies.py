from __future__ import annotations

from typing import Annotated

from app.api.security import require_librarian_or_admin
from app.deps import get_db
from app.repositories import CopyRepository
from app.schemas import CopyCreate, CopyRead
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/books/{book_id}/copies", tags=["Copies"])


@router.post(
    "", response_model=CopyRead, status_code=201, dependencies=[Depends(require_librarian_or_admin)]
)
def create_copy(book_id: int, payload: CopyCreate, db: Annotated[Session, Depends(get_db)]):
    repo = CopyRepository(db)
    c = repo.create(
        book_id=book_id,
        inventory_code=payload.inventory_code,
        status=payload.status,
    )
    db.commit()
    db.refresh(c)
    return c


@router.get("", response_model=list[CopyRead])
def list_copies(
    db: Annotated[Session, Depends(get_db)], book_id: int, limit: int = 100, offset: int = 0
):
    repo = CopyRepository(db)
    return repo.list_by_book(book_id, limit=limit, offset=offset)
