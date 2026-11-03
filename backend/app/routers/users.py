"""User endpoints; open to everyone, since the caller picks an identity on the login screen."""

from fastapi import APIRouter, status

from app.dependencies import DbSession
from app.models import User
from app.schemas.user import UserCreate, UserRead
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserRead)
def create_user(body: UserCreate, db: DbSession) -> User:
    return user_service.create_user(db, body)


@router.get("", response_model=list[UserRead])
def list_users(db: DbSession) -> list[User]:
    return user_service.list_users(db)
