from datetime import datetime

from sqlalchemy import CheckConstraint, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.enums import SplitType
from app.models.group import Group
from app.models.user import User

DESCRIPTION_MAX_LENGTH = 200


class Expense(Base):
    __tablename__ = "expenses"
    __table_args__ = (CheckConstraint("amount_cents > 0", name="expense_amount_positive"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))
    payer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    description: Mapped[str] = mapped_column(String(DESCRIPTION_MAX_LENGTH))
    amount_cents: Mapped[int]
    split_type: Mapped[SplitType] = mapped_column(Enum(SplitType))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    group: Mapped[Group] = relationship()
    payer: Mapped[User] = relationship()
    shares: Mapped[list["ExpenseShare"]] = relationship(
        back_populates="expense", cascade="all, delete-orphan"
    )


class ExpenseShare(Base):
    """One participant's part of an expense."""

    __tablename__ = "expense_shares"
    __table_args__ = (CheckConstraint("share_cents >= 0", name="share_not_negative"),)

    expense_id: Mapped[int] = mapped_column(ForeignKey("expenses.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    share_cents: Mapped[int]
    # Kept for percentage splits so the API can show the requested percentage.
    percentage_basis_points: Mapped[int | None]

    expense: Mapped[Expense] = relationship(back_populates="shares")
    user: Mapped[User] = relationship()
