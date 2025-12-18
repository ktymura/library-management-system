from datetime import datetime
from enum import Enum

from app.db import Base
from sqlalchemy import DateTime, Integer
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column


class LoanStatus(str, Enum):
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    copy_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)

    status: Mapped[LoanStatus] = mapped_column(
        SAEnum(LoanStatus, name="loan_status"),
        nullable=False,
        default=LoanStatus.ACTIVE,
    )

    loaned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    returned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
