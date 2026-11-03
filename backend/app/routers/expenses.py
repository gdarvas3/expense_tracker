from fastapi import APIRouter, status

from app.dependencies import DbSession, GroupMember
from app.models import Expense
from app.schemas.expense import ExpenseCreate, ExpenseRead
from app.services import expense_service

router = APIRouter(prefix="/groups/{group_id}/expenses", tags=["expenses"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ExpenseRead)
def create_expense(body: ExpenseCreate, membership: GroupMember, db: DbSession) -> Expense:
    return expense_service.create_expense(db, membership.group, body)


@router.get("", response_model=list[ExpenseRead])
def list_expenses(membership: GroupMember, db: DbSession) -> list[Expense]:
    return expense_service.list_expenses(db, membership.group)
