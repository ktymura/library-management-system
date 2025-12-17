from typing import Annotated

from app.core.security import create_access_token, get_password_hash, verify_password
from app.deps import get_db
from app.models.user import User
from app.schemas.auth import Token, UserLogin
from app.schemas.error import ErrorResponse
from app.schemas.user import UserCreate, UserPublic, UserRole
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

router = APIRouter()

responses = {
    401: {"model": ErrorResponse, "description": "Unauthorized"},
    409: {"model": ErrorResponse, "description": "Conflict"},
    422: {"model": ErrorResponse, "description": "Validation error"},
}


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserPublic, responses=responses
)
def register(payload: UserCreate, db: Annotated[Session, Depends(get_db)]) -> UserPublic:
    user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        is_active=True,
        role=UserRole.READER,
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


@router.post(
    "/login",
    response_model=Token,
    responses=responses,
)
def login(payload: UserLogin, db: Annotated[Session, Depends(get_db)]) -> Token:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
        )

    # sub = user.id (string)
    access = create_access_token(subject=str(user.id), role=user.role.value)
    return Token(access_token=access)
