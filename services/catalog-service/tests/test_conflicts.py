from fastapi.testclient import TestClient
from jose import jwt


def make_token(role: str) -> str:
    payload = {
        "sub": "testuser",
        "role": role,
        "iss": "lms-user-service",
        "aud": "lms-catalog-service",
    }
    return jwt.encode(payload, "supersecret", algorithm="HS256")


def test_duplicate_isbn_returns_409(client: TestClient):
    # author
    r = client.post("/authors", json={"full_name": "A"})
    assert r.status_code == 201, r.text
    author_id = r.json()["id"]

    token = make_token("LIBRARIAN")

    payload = {
        "title": "B1",
        "author_id": author_id,
        "isbn": "9780441478125",
        "published_year": 1969,
    }
    r1 = client.post("/books", headers={"Authorization": f"Bearer {token}"}, json=payload)
    assert r1.status_code == 201, r1.text

    payload2 = {
        "title": "B2",
        "author_id": author_id,
        "isbn": "9780441478125",
        "published_year": 1970,
    }
    r2 = client.post("/books", headers={"Authorization": f"Bearer {token}"}, json=payload2)
    assert r2.status_code == 409, r2.text


def test_duplicate_inventory_code_returns_409(client: TestClient):
    r = client.post("/authors", json={"full_name": "A"})
    assert r.status_code == 201, r.text
    author_id = r.json()["id"]

    token = make_token("LIBRARIAN")
    r = client.post(
        "/books",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "B", "author_id": author_id, "isbn": "9788375799132"},
    )
    book_id = r.json()["id"]

    r1 = client.post(
        f"/books/{book_id}/copies",
        headers={"Authorization": f"Bearer {token}"},
        json={"inventory_code": "INV-0001"},
    )
    assert r1.status_code == 201, r1.text

    r2 = client.post(
        f"/books/{book_id}/copies",
        headers={"Authorization": f"Bearer {token}"},
        json={"inventory_code": "INV-0001"},
    )
    assert r2.status_code == 409, r2.text


def test_get_copies_for_missing_book_returns_404(client: TestClient):
    r = client.get("/books/999/copies")
    assert r.status_code == 404
