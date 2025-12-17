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


def test_happy_path_add_copy_and_list(client: TestClient):
    # 1) autor
    r = client.post("/authors", json={"full_name": "Ursula K. Le Guin"})
    assert r.status_code == 201, r.text
    author_id = r.json()["id"]

    # 2) książka (wymaga LIBRARIAN)
    token = make_token("LIBRARIAN")
    r = client.post(
        "/books",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "The Left Hand of Darkness",
            "author_id": author_id,
            "isbn": "9780241656990",
            "published_year": 1969,
        },
    )
    assert r.status_code == 201, r.text
    book_id = r.json()["id"]

    # 3) kopia (LIBRARIAN)
    r = client.post(
        f"/books/{book_id}/copies",
        headers={"Authorization": f"Bearer {token}"},
        json={"inventory_code": "INV-0001"},
    )
    assert r.status_code == 201, r.text

    # 4) lista kopii
    r = client.get(f"/books/{book_id}/copies")
    assert r.status_code == 200, r.text
    copies = r.json()
    assert len(copies) == 1
    assert copies[0]["inventory_code"] == "INV-0001"


def test_forbidden_without_required_role(client: TestClient):
    token = make_token("READER")
    # READER nie może tworzyć książki
    r = client.post(
        "/books",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "X", "author_id": 1},
    )
    assert r.status_code == 403
