import pytest
from app.main import app
from app.models.loan import Loan, LoanStatus
from fastapi.testclient import TestClient
from jose import jwt


def make_token(role: str) -> str:
    payload = {
        "sub": "testuser",
        "role": role,
        "iss": "lms-user-service",
        "aud": "lms",
    }
    return jwt.encode(payload, "supersecret", algorithm="HS256")


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def test_return_loan_success(client, db_session, monkeypatch):
    # stub catalog call
    called = {}

    def fake_set_copy_status(copy_id: int, status: str) -> None:
        called["copy_id"] = copy_id
        called["status"] = status

    monkeypatch.setattr("app.services.loans._catalog_set_copy_status", fake_set_copy_status)

    # create ACTIVE loan in DB
    loan = Loan(user_id=1, copy_id=12, status=LoanStatus.ACTIVE, returned_at=None)
    db_session.add(loan)
    db_session.commit()
    db_session.refresh(loan)

    token = make_token("LIBRARIAN")
    r = client.post(f"/loans/{loan.id}/return", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.text
    data = r.json()

    assert data["id"] == loan.id
    assert data["copy_id"] == 12
    assert data["user_id"] == 1
    assert data["status"] == "LoanStatus.RETURNED" or data["status"] == "RETURNED"
    assert data["returned_at"] is not None

    # ensure we attempted to set copy AVAILABLE in catalog
    assert called == {"copy_id": 12, "status": "AVAILABLE"}

    # verify DB state
    db_session.refresh(loan)
    assert loan.status == LoanStatus.RETURNED
    assert loan.returned_at is not None


def test_return_loan_not_found(client, monkeypatch):
    monkeypatch.setattr("app.services.loans._catalog_set_copy_status", lambda *args, **kwargs: None)

    token = make_token("LIBRARIAN")
    r = client.post("/loans/999999/return", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 404, r.text


def test_return_loan_already_returned(client, db_session, monkeypatch):
    monkeypatch.setattr("app.services.loans._catalog_set_copy_status", lambda *args, **kwargs: None)

    loan = Loan(user_id=1, copy_id=15, status=LoanStatus.RETURNED)
    db_session.add(loan)
    db_session.commit()
    db_session.refresh(loan)

    token = make_token("LIBRARIAN")
    r = client.post(f"/loans/{loan.id}/return", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 409, r.text
