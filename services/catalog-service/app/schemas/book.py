from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.utils.validators import validate_isbn, validate_year


class BookCreate(BaseModel):
    title: str
    author_id: int
    isbn: str | None = None
    published_year: int | None = None

    @field_validator("isbn")
    @classmethod
    def _isbn_ok(cls, v: str | None) -> str | None:
        return validate_isbn(v)

    @field_validator("published_year")
    @classmethod
    def _year_ok(cls, v: int | None) -> int | None:
        return validate_year(v)


class BookUpdate(BaseModel):
    title: str | None = None
    author_id: int | None = None
    isbn: str | None = None
    published_year: int | None = None

    @field_validator("isbn")
    @classmethod
    def _isbn_ok(cls, v: str | None) -> str | None:
        return validate_isbn(v)

    @field_validator("published_year")
    @classmethod
    def _year_ok(cls, v: int | None) -> int | None:
        return validate_year(v)


class BookRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    isbn: str | None
    published_year: int | None
    author_id: int
    created_at: datetime
    updated_at: datetime
