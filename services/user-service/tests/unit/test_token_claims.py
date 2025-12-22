import os

from app.core.security import create_access_token
from jose import jwt


def test_token_contains_role_iss_aud():
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
        audience="lms",
        options={"verify_aud": True},
    )

    assert claims["sub"] == "42"
    assert claims["role"] == "LIBRARIAN"
    assert claims["iss"] == "lms-user-service"
    assert claims["aud"] == "lms"
    assert "exp" in claims
