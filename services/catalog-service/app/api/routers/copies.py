from __future__ import annotations

from typing import Annotated

from app.api.security import require_librarian_or_admin
from app.deps import get_db
from app.models import CopyStatus
from app.repositories import CopyRepository
from app.schemas import CopyCreate, CopyRead, ErrorResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

RESP_401_403 = {
    401: {"model": ErrorResponse, "description": "Unauthorized (missing/invalid JWT)"},
    403: {"model": ErrorResponse, "description": "Forbidden (insufficient role)"},
}
RESP_404 = {404: {"model": ErrorResponse, "description": "Not found"}}
RESP_409 = {409: {"model": ErrorResponse, "description": "Conflict (already exists)"}}
router = APIRouter(prefix="/books/{book_id}/copies", tags=["Copies"])


@router.post(
    "",
    response_model=CopyRead,
    status_code=201,
    dependencies=[Depends(require_librarian_or_admin)],
    responses={**RESP_401_403, **RESP_404, **RESP_409},
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


@router.get("", response_model=list[CopyRead], responses={**RESP_401_403, **RESP_404, **RESP_409})
def list_copies(
    db: Annotated[Session, Depends(get_db)], book_id: int, limit: int = 100, offset: int = 0
):
    repo = CopyRepository(db)
    return repo.list_by_book(book_id, limit=limit, offset=offset)


@router.get("/{copy_id}", response_model=CopyRead, responses={**RESP_401_403, **RESP_404})
def get_copy(copy_id: int, db: Annotated[Session, Depends(get_db)]):
    repo = CopyRepository(db)
    c = repo.get(copy_id)  # jeśli metoda nazywa się inaczej, zmień
    if not c:
        raise HTTPException(status_code=404, detail="Copy not found")
    return c


@router.patch(
    "/{copy_id}",
    response_model=CopyRead,
    dependencies=[Depends(require_librarian_or_admin)],
    responses={**RESP_401_403, **RESP_404},
)
def update_copy_status(copy_id: int, payload: dict, db: Annotated[Session, Depends(get_db)]):
    new_status = payload.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Missing status")

    # walidacja enum
    try:
        CopyStatus(new_status)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid status") from exc

    repo = CopyRepository(db)
    c = repo.get(copy_id)
    if not c:
        raise HTTPException(status_code=404, detail="Copy not found")

    c.status = new_status
    db.commit()
    db.refresh(c)
    return c
