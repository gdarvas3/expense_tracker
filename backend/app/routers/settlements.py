"""Settlements, balances and the simplified settlement plan of a group."""

from fastapi import APIRouter, status

from app.dependencies import DbSession, GroupMember
from app.models import Settlement
from app.schemas.balance import BalanceRead, TransferRead
from app.schemas.settlement import SettlementCreate, SettlementRead
from app.services import settlement_service
from app.services.balance_service import calculate_balances
from app.services.settlement import Transfer

router = APIRouter(prefix="/groups/{group_id}", tags=["settlements"])


@router.post("/settlements", status_code=status.HTTP_201_CREATED, response_model=SettlementRead)
def record_settlement(
    body: SettlementCreate, membership: GroupMember, db: DbSession
) -> Settlement:
    return settlement_service.record_settlement(db, membership.group, body)


@router.get("/balances", response_model=list[BalanceRead])
def get_balances(membership: GroupMember, db: DbSession) -> list[BalanceRead]:
    balances = calculate_balances(db, membership.group)
    return [
        BalanceRead(user_id=user_id, net_cents=net_cents)
        for user_id, net_cents in sorted(balances.items())
    ]


@router.get("/settlement-plan", response_model=list[TransferRead])
def get_settlement_plan(membership: GroupMember, db: DbSession) -> list[Transfer]:
    return settlement_service.settlement_plan(db, membership.group)
