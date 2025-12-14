from typing import Annotated

from app.deps_auth import get_current_user, require_role
from app.models.user import User, UserRole
from app.schemas.error import ErrorResponse
from app.schemas.user import UserPublic
from fastapi import APIRouter, Depends

router = APIRouter()
responses_me = {
    401: {"model": ErrorResponse, "description": "Unauthorized"},
    422: {"model": ErrorResponse, "description": "Validation error"},
}


@router.get("/me", response_model=UserPublic, responses=responses_me)
def read_me(current_user: Annotated[User, Depends(get_current_user)]) -> UserPublic:
    return current_user


@router.get("/admin/ping", responses=responses_me)
def admin_ping(_: Annotated[User, Depends(require_role(UserRole.ADMIN))]):
    return {"ok": True}
