from typing import Annotated

from app.deps import get_db
from app.deps_auth import get_current_user, require_role
from app.models.user import User, UserRole
from app.schemas.error import ErrorResponse
from app.schemas.user import RoleUpdate, UserPublic
from app.services.users import get_users, set_user_role
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["users"])
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


@router.get("", response_model=list[UserPublic])
def list_users(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[UserPublic]:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")

    return get_users(db)


@router.patch("/{user_id}/role", status_code=204)
def update_role(
    user_id: int,
    payload: RoleUpdate,
    db: Annotated[Session, Depends(get_db)],
    current: Annotated[User, Depends(get_current_user)],
):
    if current.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")

    set_user_role(db, user_id, payload.role)
    return None
