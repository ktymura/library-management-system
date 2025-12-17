from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuthorCreate(BaseModel):
    full_name: str


class AuthorUpdate(BaseModel):
    full_name: str | None = None


class AuthorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    created_at: datetime
    updated_at: datetime
