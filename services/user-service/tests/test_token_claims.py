import os

from app.core.security import create_access_token
from jose import jwt


def test_token_contains_role_iss_aud(monkeypatch):
    # ustaw konfig na test
    monkeypatch.setenv("JWT_SECRET", "supersecret")
    monkeypatch.setenv("JWT_ALG", "HS256")
    monkeypatch.setenv("JWT_EXPIRES_MIN", "60")
    monkeypatch.setenv("JWT_ISSUER", "lms-user-service")
    monkeypatch.setenv("JWT_AUDIENCE", "lms-catalog-service")

    token = create_access_token(
        subject="42",
        role="LIBRARIAN",
        extra={"email": "lib@test.pl"},
        expires_minutes=5,
    )

    claims = jwt.decode(
        token,
        "supersecret",
        algorithms=["HS256"],
        issuer="lms-user-service",
        audience="lms-catalog-service",
        options={"verify_aud": True},
    )

    assert claims["sub"] == "42"
    assert claims["role"] == "LIBRARIAN"
    assert claims["iss"] == "lms-user-service"
    assert claims["aud"] == "lms-catalog-service"
    assert "exp" in claims
