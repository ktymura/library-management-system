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


def test_given_book_and_copy_when_add_copy_then_get_books_id_copies_returns_it(client: TestClient):
    token = make_token("LIBRARIAN")
    # author
    r = client.post(
        "/authors",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Ursula K. Le Guin"},
    )
    assert r.status_code == 201, r.text
    author_id = r.json()["id"]

    # book
    r = client.post(
        "/books",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "The Left Hand of Darkness",
            "author_id": author_id,
            "isbn": "9788382526943",
            "published_year": 1969,
        },
    )
    # assert r.status_code == 201, r.text
    book_id = r.json()["id"]
    # add copy
    r = client.post(
        f"/books/{book_id}/copies",
        headers={"Authorization": f"Bearer {token}"},
        json={"inventory_code": "INV-0001"},
    )
    assert r.status_code == 201, r.text

    # list copies
    r = client.get(f"/books/{book_id}/copies")
    assert r.status_code == 200, r.text
    copies = r.json()
    assert any(c["inventory_code"] == "INV-0001" for c in copies)
