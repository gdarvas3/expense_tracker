"""Tests for request/response schemas: decimal JSON values ↔ integer cents and basis points."""

from datetime import UTC, datetime

import pydantic
import pytest

from app.enums import SplitType
from app.schemas.expense import ExpenseCreate, ExpenseRead, ShareRead
from app.schemas.settlement import SettlementCreate

VALID_EXPENSE: dict[str, object] = {
    "description": "Groceries",
    "amount": "100.00",
    "payer_id": 1,
    "split_type": "percentage",
    "participants": [
        {"user_id": 1, "percentage": "33.33"},
        {"user_id": 2, "percentage": "66.67"},
    ],
}


def expense_with(**overrides: object) -> dict[str, object]:
    return {**VALID_EXPENSE, **overrides}


def test_expense_create_converts_amount_to_cents_and_percentages_to_basis_points() -> None:
    expense = ExpenseCreate.model_validate(VALID_EXPENSE)

    assert expense.amount_cents == 10000
    assert expense.split_type is SplitType.PERCENTAGE
    assert expense.participants[0].percentage_basis_points == 3333
    assert expense.participants[1].percentage_basis_points == 6667


def test_expense_create_accepts_exact_share_amounts() -> None:
    expense = ExpenseCreate.model_validate(
        expense_with(split_type="exact", participants=[{"user_id": 1, "amount": "40.50"}])
    )

    assert expense.participants[0].share_cents == 4050


@pytest.mark.parametrize("amount", ["0", "0.00", "-1.00"])
def test_expense_create_rejects_non_positive_amount(amount: str) -> None:
    # AC-5: amount <= 0 is invalid.
    with pytest.raises(pydantic.ValidationError):
        ExpenseCreate.model_validate(expense_with(amount=amount))


@pytest.mark.parametrize(
    "invalid_fields",
    [
        {"amount": "10.001"},
        {"split_type": "random"},
        {"participants": []},
        {"unexpected": "field"},
    ],
)
def test_expense_create_rejects_malformed_input(invalid_fields: dict[str, object]) -> None:
    with pytest.raises(pydantic.ValidationError):
        ExpenseCreate.model_validate(expense_with(**invalid_fields))


def test_settlement_create_rejects_non_positive_amount() -> None:
    with pytest.raises(pydantic.ValidationError):
        SettlementCreate.model_validate({"payer_id": 2, "payee_id": 1, "amount": "0"})


def test_expense_read_serializes_cents_as_decimal_strings() -> None:
    expense = ExpenseRead(
        id=7,
        description="Groceries",
        amount_cents=10000,
        payer_id=1,
        split_type=SplitType.PERCENTAGE,
        created_at=datetime(2026, 11, 3, tzinfo=UTC),
        shares=[ShareRead(user_id=1, share_cents=3333, percentage_basis_points=3333)],
    )

    payload = expense.model_dump(mode="json", by_alias=True)

    assert payload["amount"] == "100.00"
    assert payload["shares"] == [{"user_id": 1, "amount": "33.33", "percentage": "33.33"}]
