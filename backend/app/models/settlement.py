from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.group import Group
from app.models.user import User


class Settlement(Base):
    """A direct payment from one member to another that reduces their debt (AC-8)."""

    __tablename__ = "settlements"
    __table_args__ = (
        CheckConstraint("amount_cents > 0", name="settlement_amount_positive"),
        CheckConstraint("payer_id <> payee_id", name="settlement_distinct_parties"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))
    payer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    payee_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount_cents: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    group: Mapped[Group] = relationship()
    payer: Mapped[User] = relationship(foreign_keys=[payer_id])
    payee: Mapped[User] = relationship(foreign_keys=[payee_id])
