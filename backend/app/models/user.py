from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

NAME_MAX_LENGTH = 100


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH), unique=True)
