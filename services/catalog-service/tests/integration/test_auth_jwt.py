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


def test_create_book_requires_token(client: TestClient):
    r = client.post("/books", json={"title": "X", "author_id": 1})
    assert r.status_code == 401


def test_create_book_forbidden_for_reader(client: TestClient):
    token = make_token("READER")
    r = client.post(
        "/books",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "X", "author_id": 1},
    )
    assert r.status_code == 403
