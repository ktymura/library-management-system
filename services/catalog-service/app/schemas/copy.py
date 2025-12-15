from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.copy import CopyStatus  # użyjemy tego samego Enum co w modelu


class CopyCreate(BaseModel):
    inventory_code: str
    status: CopyStatus | None = None  # domyślnie AVAILABLE po stronie modelu


class CopyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    inventory_code: str
    status: CopyStatus
    book_id: int
    created_at: datetime
    updated_at: datetime
