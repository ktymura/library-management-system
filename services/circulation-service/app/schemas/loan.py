from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class LoanCreate(BaseModel):
    copy_id: int
    user_id: int


class LoanRead(BaseModel):
    id: int
    copy_id: int
    user_id: int
    status: str
    loaned_at: datetime
    returned_at: datetime | None
