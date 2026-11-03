from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions import ValidationError
from app.models import Expense, ExpenseShare, Group
from app.schemas.expense import ExpenseCreate, ParticipantInput
from app.services.membership import ensure_members
from app.services.split import calculate_shares


def create_expense(db: Session, group: Group, data: ExpenseCreate) -> Expense:
    """Record an expense and its per-participant shares.

    Raises:
        ValidationError: If the payer or a participant is not a member, a participant is
            listed twice, or the split is invalid (AC-5).
    """
    participant_ids = [participant.user_id for participant in data.participants]
    ensure_members(group, [data.payer_id, *participant_ids])
    if len(set(participant_ids)) != len(participant_ids):
        raise ValidationError("Each participant may be listed only once.")

    shares = calculate_shares(data.amount_cents, data.split_type, data.participants)
    expense = Expense(
        group=group,
        payer_id=data.payer_id,
        description=data.description,
        amount_cents=data.amount_cents,
        split_type=data.split_type,
        shares=[build_share(participant, shares) for participant in data.participants],
    )
    db.add(expense)
    db.commit()
    return expense


def build_share(participant: ParticipantInput, shares: dict[int, int]) -> ExpenseShare:
    return ExpenseShare(
        user_id=participant.user_id,
        share_cents=shares[participant.user_id],
        percentage_basis_points=participant.percentage_basis_points,
    )


def list_expenses(db: Session, group: Group) -> list[Expense]:
    query = select(Expense).where(Expense.group_id == group.id).order_by(Expense.id)
    return list(db.scalars(query))
