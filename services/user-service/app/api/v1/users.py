from typing import Annotated

from app.deps_auth import get_current_user
from app.models.user import User
from app.schemas.user import UserPublic
from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/me", response_model=UserPublic)
def read_me(current_user: Annotated[User, Depends(get_current_user)]) -> UserPublic:
    return current_user
