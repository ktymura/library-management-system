from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DemoAuthor:
    full_name: str


@dataclass(frozen=True)
class DemoBook:
    key: str
    title: str
    isbn: str
    published_year: int | None
    author_full_name: str


@dataclass(frozen=True)
class DemoCopy:
    inventory_code: str
    book_key: str
    status: str = "AVAILABLE"


DEMO_AUTHORS: list[DemoAuthor] = [
    DemoAuthor(full_name="Andrzej Sapkowski"),
    DemoAuthor(full_name="Stanisław Lem"),
]

DEMO_BOOKS: list[DemoBook] = [
    DemoBook(
        key="witcher_last_wish",
        title="Ostatnie życzenie",
        isbn="9788375780635",
        published_year=1993,
        author_full_name="Andrzej Sapkowski",
    ),
    DemoBook(
        key="lem_solaris",
        title="Solaris",
        isbn="9788308062901",
        published_year=1961,
        author_full_name="Stanisław Lem",
    ),
]

DEMO_COPIES: list[DemoCopy] = [
    DemoCopy(inventory_code="DEMO-WS-0001", book_key="witcher_last_wish"),
    DemoCopy(inventory_code="DEMO-WS-0002", book_key="witcher_last_wish"),
    DemoCopy(inventory_code="DEMO-SL-0001", book_key="lem_solaris"),
]
