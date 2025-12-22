from __future__ import annotations

import os
from datetime import datetime, timezone

from app.seed.constants import DEMO_LOANS
from sqlalchemy.orm import Session


def seed_demo_loans(db: Session) -> dict[str, int]:
    from app.models.loan import Loan, LoanStatus

    created = 0
    skipped = 0

    for loan in DEMO_LOANS:
        user_id = loan.user_id_default
        copy_id = loan.copy_id_default
        status = LoanStatus(loan.status)

        existing = (
            db.query(Loan)
            .filter(
                Loan.user_id == user_id,
                Loan.copy_id == copy_id,
                Loan.status == status,
            )
            .first()
        )
        if existing:
            skipped += 1
            continue

        loan = Loan(
            user_id=user_id,
            copy_id=copy_id,
            status=status,
            loaned_at=datetime.now(timezone.utc),
        )

        if status == LoanStatus.RETURNED:
            loan.returned_at = datetime.now(timezone.utc)

        db.add(loan)
        created += 1

    db.commit()
    return {"created": created, "skipped": skipped}
