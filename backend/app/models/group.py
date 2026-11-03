from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.enums import MemberRole
from app.models.user import User

GROUP_NAME_MAX_LENGTH = 100


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(GROUP_NAME_MAX_LENGTH))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="group", cascade="all, delete-orphan"
    )


class Membership(Base):
    """Links a user to a group; the composite primary key prevents duplicate membership."""

    __tablename__ = "memberships"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role: Mapped[MemberRole] = mapped_column(Enum(MemberRole))

    group: Mapped[Group] = relationship(back_populates="memberships")
    user: Mapped[User] = relationship()
