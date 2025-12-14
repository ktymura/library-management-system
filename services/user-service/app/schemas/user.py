from pydantic import BaseModel, EmailStr, Field


# payload rejestracji
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


# to zwracamy na zewnątrz (bez hasła)
class UserPublic(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    is_active: bool

    class Config:
        from_attributes = True
