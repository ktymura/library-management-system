from __future__ import annotations

import pytest
import requests
from app.main import app
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


def test_create_loan_success_copy_available(monkeypatch, client):
    # catalog: GET -> AVAILABLE, PATCH -> OK

    class Resp:
        def __init__(self, status_code: int, json_data=None, text=""):
            self.status_code = status_code
            self._json_data = json_data or {}
            self.text = text

        def json(self):
            return self._json_data

    def fake_get(url, headers=None, timeout=None):
        return Resp(200, {"id": 10, "status": "AVAILABLE"})

    def fake_patch(url, json=None, headers=None, timeout=None):
        assert json == {"status": "LOANED"}
        return Resp(200, {"id": 10, "status": "LOANED"})

    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(requests, "patch", fake_patch)
    token = make_token("LIBRARIAN")
    r = client.post(
        "/loans", json={"copy_id": 10, "user_id": 5}, headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["copy_id"] == 10
    assert data["user_id"] == 5
    assert data["status"] == "LoanStatus.ACTIVE" or data["status"] == "ACTIVE"


def test_create_loan_fails_when_copy_already_loaned(monkeypatch, client):
    # catalog: GET -> LOANED

    class Resp:
        def __init__(self, status_code: int, json_data=None, text=""):
            self.status_code = status_code
            self._json_data = json_data or {}
            self.text = text

        def json(self):
            return self._json_data

    def fake_get(url, headers=None, timeout=None):
        return Resp(200, {"id": 10, "status": "LOANED"})

    monkeypatch.setattr(requests, "get", fake_get)
    token = make_token("LIBRARIAN")
    r = client.post(
        "/loans", json={"copy_id": 10, "user_id": 5}, headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 400, r.text
    assert "not available" in r.json()["detail"].lower()
