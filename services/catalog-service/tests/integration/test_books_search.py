from __future__ import annotations

from app.repositories import AuthorRepository, BookRepository
from fastapi.testclient import TestClient


def _global_seed(db):
    a_repo = AuthorRepository(db)
    b_repo = BookRepository(db)

    # zabezpieczenie przed duplikacją przy ponownym imporcie
    try:
        rowling = a_repo.create(full_name="J. K. Rowling")
        sapkowski = a_repo.create(full_name="Andrzej Sapkowski")
        db.flush()

        b_repo.create(
            title="Harry Potter i Kamień Filozoficzny",
            author_id=rowling.id,
            isbn="isbn-hp-1",
            published_year=1997,
        )
        b_repo.create(
            title="Wiedźmin: Ostatnie życzenie",
            author_id=sapkowski.id,
            isbn="isbn-wiedzmin-1",
            published_year=1993,
        )
        db.commit()
    except Exception:
        # dane już istnieją — OK
        db.rollback()


def test_search_by_title(client: TestClient, db_session):
    _global_seed(db_session)

    r = client.get("/books/search", params={"query": "Harry"})
    assert r.status_code == 200
    data = r.json()
    assert any("Harry" in item["title"] for item in data)


def test_search_by_author(client: TestClient, db_session):
    _global_seed(db_session)

    r = client.get("/books/search", params={"query": "Sapkowski"})
    assert r.status_code == 200
    data = r.json()
    assert any("Wiedźmin" in item["title"] for item in data)


def test_search_no_results(client: TestClient, db_session):
    _global_seed(db_session)

    r = client.get("/books/search", params={"query": "nieistnieje-xyz"})
    assert r.status_code == 200
    assert r.json() == []


def test_search_blank_query_returns_422(client: TestClient, db_session):
    _global_seed(db_session)

    r = client.get("/books/search", params={"query": "   "})
    assert r.status_code == 422
