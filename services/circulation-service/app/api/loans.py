from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.security import get_current_user_claims, require_librarian_or_admin
from app.deps import get_db
from app.schemas.loan import LoanCreate, LoanRead
from app.services.loans import (
    CatalogServiceError,
    CopyNotAvailableError,
    CopyNotFoundError,
    create_loan,
)

router = APIRouter(prefix="/loans", tags=["Loans"])


@router.post(
    "",
    response_model=LoanRead,
    status_code=201,
    dependencies=[Depends(require_librarian_or_admin)],
)
def create_loan_endpoint(
    payload: LoanCreate,
    db: Annotated[Session, Depends(get_db)],
):
    try:
        result = create_loan(db=db, copy_id=payload.copy_id, user_id=payload.user_id)
        loan = result.loan
        return LoanRead(
            id=loan.id,
            copy_id=loan.copy_id,
            user_id=loan.user_id,
            status=str(loan.status),
            loaned_at=loan.loaned_at,
            returned_at=loan.returned_at,
        )
    except CopyNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except CopyNotAvailableError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except CatalogServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
