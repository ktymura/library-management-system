from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DemoLoan:
    key: str
    user_id_default: int
    copy_id_default: int
    status: str = "ACTIVE"


DEMO_LOANS: list[DemoLoan] = [
    DemoLoan(key="loan_1", user_id_default=2, copy_id_default=1, status="ACTIVE"),
    DemoLoan(key="loan_2", user_id_default=2, copy_id_default=3, status="RETURNED"),
]
