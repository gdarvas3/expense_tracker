from sqlalchemy.orm import Session

from app.exceptions import ValidationError
from app.models import Group, Settlement
from app.schemas.settlement import SettlementCreate
from app.services.balance_service import calculate_balances
from app.services.membership import ensure_members
from app.services.settlement import Transfer, simplify_debts


def record_settlement(db: Session, group: Group, data: SettlementCreate) -> Settlement:
    """Record a direct payment between two members (AC-8).

    Raises:
        ValidationError: If payer and payee are the same or not both members.
    """
    if data.payer_id == data.payee_id:
        raise ValidationError("Payer and payee must be different members.")
    ensure_members(group, [data.payer_id, data.payee_id])
    settlement = Settlement(
        group=group,
        payer_id=data.payer_id,
        payee_id=data.payee_id,
        amount_cents=data.amount_cents,
    )
    db.add(settlement)
    db.commit()
    return settlement


def settlement_plan(db: Session, group: Group) -> list[Transfer]:
    """Return the simplified list of payments that settles every balance (AC-4)."""
    return simplify_debts(calculate_balances(db, group))
