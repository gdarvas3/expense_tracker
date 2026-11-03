"""Net balances of group members, derived from expenses and settlements."""

from collections import defaultdict
from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Expense, Group, Settlement
from app.services.membership import member_ids


def calculate_balances(db: Session, group: Group) -> dict[int, int]:
    """Return each member's net balance in cents; positive means the others owe them."""
    expenses = db.scalars(
        select(Expense).where(Expense.group_id == group.id).options(selectinload(Expense.shares))
    )
    settlements = db.scalars(select(Settlement).where(Settlement.group_id == group.id))
    return net_balances(member_ids(group), expenses, settlements)


def net_balances(
    member_ids: Iterable[int], expenses: Iterable[Expense], settlements: Iterable[Settlement]
) -> dict[int, int]:
    """Compute net balances: paid − consumed + settlements paid − settlements received.

    Only current members are returned; removed members always net to zero (AC-6 rule).
    """
    totals: defaultdict[int, int] = defaultdict(int)
    for expense in expenses:
        totals[expense.payer_id] += expense.amount_cents
        for share in expense.shares:
            totals[share.user_id] -= share.share_cents
    for settlement in settlements:
        totals[settlement.payer_id] += settlement.amount_cents
        totals[settlement.payee_id] -= settlement.amount_cents
    return {user_id: totals[user_id] for user_id in member_ids}
