import re
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, field_validator

# min i max długość hasła
PW_MIN = 8
PW_MAX = 72

_re_upper = re.compile(r"[A-Z]")
_re_lower = re.compile(r"[a-z]")
_re_digit = re.compile(r"\d")
_re_special = re.compile(r"[^A-Za-z0-9]")


class UserRole(str, Enum):
    READER = "READER"
    LIBRARIAN = "LIBRARIAN"
    ADMIN = "ADMIN"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=PW_MIN,
        max_length=PW_MAX,
        description="8–72 znaków, min. jedna: mała, wielka, cyfra i znak specjalny",
    )

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        # Limit bcrypt dotyczy bajtów; dla zwykłych ASCII == len(str)
        if len(v.encode("utf-8")) > PW_MAX:
            raise ValueError("Password is too long.")
        rules = [
            (_re_lower.search(v), "lowercase letter"),
            (_re_upper.search(v), "uppercase letter"),
            (_re_digit.search(v), "digit"),
            (_re_special.search(v), "special character"),
        ]
        missing = [name for ok, name in rules if not ok]
        if missing:
            raise ValueError("Password must contain at least one " + ", ".join(missing) + ".")
        return v


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    is_active: bool
    role: UserRole

    class Config:
        from_attributes = True
