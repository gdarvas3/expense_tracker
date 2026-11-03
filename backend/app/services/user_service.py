from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions import ConflictError
from app.models import User
from app.schemas.user import UserCreate


def create_user(db: Session, data: UserCreate) -> User:
    """Create a user with a unique name.

    Raises:
        ConflictError: If the name is already taken.
    """
    if db.scalar(select(User).where(User.name == data.name)) is not None:
        raise ConflictError(f"User name '{data.name}' is already taken.")
    user = User(name=data.name)
    db.add(user)
    db.commit()
    return user


def list_users(db: Session) -> list[User]:
    return list(db.scalars(select(User).order_by(User.id)))
