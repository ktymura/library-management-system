# app/services/users.py
from app import User, UserRole
from sqlalchemy.orm import Session


def set_user_role(db: Session, user_id: int, role: UserRole) -> None:
    user = db.get(User, user_id)
    if not user:
        raise ValueError("User not found")
    user.role = role
    db.commit()


def get_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.id).all()
