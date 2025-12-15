from __future__ import annotations

from typing import Annotated

from app.deps import get_db
from app.repositories import AuthorRepository
from app.schemas import AuthorCreate, AuthorRead
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/authors", tags=["Authors"])


@router.post("", response_model=AuthorRead, status_code=201)
def create_author(payload: AuthorCreate, db: Annotated[Session, Depends(get_db)]):
    repo = AuthorRepository(db)
    a = repo.create(full_name=payload.full_name)
    db.commit()
    db.refresh(a)
    return a


@router.get("", response_model=list[AuthorRead])
def list_authors(
    db: Annotated[Session, Depends(get_db)], q: str | None = None, limit: int = 50, offset: int = 0
):
    repo = AuthorRepository(db)
    return repo.list(q=q, limit=limit, offset=offset)


@router.get("/{author_id}", response_model=AuthorRead)
def get_author(author_id: int, db: Annotated[Session, Depends(get_db)]):
    repo = AuthorRepository(db)
    a = repo.require(author_id)
    return a
