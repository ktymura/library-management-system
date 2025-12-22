from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import requests
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.loan import Loan, LoanStatus

# --- Errors ---


class CopyNotAvailableError(Exception):
    """Copy exists but is not AVAILABLE (e.g. already LOANED)."""


class CopyNotFoundError(Exception):
    """Copy does not exist in catalog-service."""


class CatalogServiceError(Exception):
    """Catalog-service unreachable / unexpected response."""


class LoanNotFoundError(Exception):
    """Loan with given id does not exist."""


class LoanAlreadyReturnedError(Exception):
    """Loan is already RETURNED (cannot return twice)."""


@dataclass(frozen=True)
class CreateLoanResult:
    loan: Loan


# --- Catalog integration ---
def _auth_headers() -> dict:
    if not settings.SERVICE_JWT:
        raise CatalogServiceError("SERVICE_JWT is not configured")
    return {"Authorization": f"Bearer {settings.SERVICE_JWT}"}


def _catalog_get_copy_status(copy_id: int) -> str:
    base = settings.CATALOG_SERVICE_URL.rstrip("/")
    url = f"{base}/copies/{copy_id}"

    try:
        r = requests.get(url, headers=_auth_headers(), timeout=3)
    except requests.RequestException as e:
        raise CatalogServiceError("catalog-service request failed") from e

    if r.status_code == 404:
        return "NOT_FOUND"

    if r.status_code != 200:
        raise CatalogServiceError(f"catalog-service returned {r.status_code}: {r.text}")

    data = r.json()
    status = data.get("status")
    if not status:
        raise CatalogServiceError("catalog-service response missing 'status'")
    return str(status)


def _catalog_set_copy_status(copy_id: int, status: str) -> None:
    base = settings.CATALOG_SERVICE_URL.rstrip("/")
    url = f"{base}/copies/{copy_id}"

    try:
        r = requests.patch(url, json={"status": status}, headers=_auth_headers(), timeout=3)
    except requests.RequestException as e:
        raise CatalogServiceError("catalog-service request failed") from e

    if r.status_code == 404:
        raise CopyNotFoundError(f"Copy {copy_id} not found")

    if r.status_code not in (200, 204):
        raise CatalogServiceError(f"catalog-service returned {r.status_code}: {r.text}")


# --- Domain/service function ---


def create_loan(*, db: Session, copy_id: int, user_id: int) -> CreateLoanResult:
    """
    Business logic for borrowing a copy.
    Flow:
    1) Ask catalog for availability
    2) Create Loan (ACTIVE)
    3) Set catalog copy status -> LOANED
    4) If catalog update fails -> compensate (delete Loan)
    """
    if copy_id <= 0:
        raise ValueError("copy_id must be positive")
    if user_id <= 0:
        raise ValueError("user_id must be positive")

    status = _catalog_get_copy_status(copy_id)

    if status == "NOT_FOUND":
        raise CopyNotFoundError(f"Copy {copy_id} not found")

    if status != "AVAILABLE":
        raise CopyNotAvailableError(f"Copy {copy_id} is not available (status={status})")

    loan = Loan(
        copy_id=copy_id,
        user_id=user_id,
        status=LoanStatus.ACTIVE,
        loaned_at=datetime.now(timezone.utc),
        returned_at=None,
    )
    db.add(loan)
    db.flush()

    try:
        _catalog_set_copy_status(copy_id, "LOANED")
    except Exception as exc:
        db.delete(loan)
        db.flush()
        raise CatalogServiceError("Failed to update copy status in catalog-service") from exc

    db.commit()
    db.refresh(loan)
    return CreateLoanResult(loan=loan)


def return_loan(*, db: Session, loan_id: int) -> Loan:
    """
    Business logic for returning a copy.
    Flow:
    1) Load Loan
    2) Validate status (must be ACTIVE)
    3) Update Loan -> RETURNED + returned_at
    4) Set catalog copy status -> AVAILABLE
    5) If catalog update fails -> compensate (revert Loan changes)
    """
    if loan_id <= 0:
        raise ValueError("loan_id must be positive")

    loan: list[Loan | None] = db.get(Loan, loan_id)
    if loan is None:
        raise LoanNotFoundError(f"Loan {loan_id} not found")

    if loan.status == LoanStatus.RETURNED:
        raise LoanAlreadyReturnedError(f"Loan {loan_id} is already returned")

    # zapamiętujemy poprzedni stan pod kompensację
    prev_status = loan.status
    prev_returned_at = loan.returned_at

    loan.status = LoanStatus.RETURNED
    loan.returned_at = datetime.now(timezone.utc)
    db.flush()

    try:
        _catalog_set_copy_status(loan.copy_id, "AVAILABLE")
    except Exception as exc:
        # kompensacja: cofamy zmianę w Loan
        loan.status = prev_status
        loan.returned_at = prev_returned_at
        db.flush()
        raise CatalogServiceError("Failed to update copy status in catalog-service") from exc

    db.commit()
    db.refresh(loan)
    return loan
