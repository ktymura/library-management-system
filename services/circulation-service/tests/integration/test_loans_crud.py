from datetime import datetime, timezone

from app.models.loan import Loan, LoanStatus


def test_create_and_read_loan(db_session):
    loan = Loan(
        user_id=1,
        copy_id=1,
        status=LoanStatus.ACTIVE,
        loaned_at=datetime.now(timezone.utc),
        returned_at=None,
    )

    db_session.add(loan)
    db_session.commit()
    db_session.refresh(loan)

    assert loan.id is not None
    assert loan.status == LoanStatus.ACTIVE

    loaded = db_session.get(Loan, loan.id)
    assert loaded is not None
    assert loaded.user_id == 1
    assert loaded.copy_id == 1
    assert loaded.returned_at is None
