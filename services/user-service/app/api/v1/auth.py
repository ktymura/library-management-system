from typing import Annotated

from app.core.security import get_password_hash
from app.deps import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserPublic
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserPublic)
def register(payload: UserCreate, db: Annotated[Session, Depends(get_db)]) -> UserPublic:
    user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        is_active=True,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists."
        ) from err
    db.refresh(user)
    return user
