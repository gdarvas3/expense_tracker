"""Unit tests for net balance calculation from expenses and settlements."""

from app.enums import SplitType
from app.models import Expense, ExpenseShare, Settlement
from app.services.balance_service import net_balances


def expense(payer_id: int, shares: dict[int, int]) -> Expense:
    return Expense(
        payer_id=payer_id,
        description="Test",
        amount_cents=sum(shares.values()),
        split_type=SplitType.EXACT,
        shares=[
            ExpenseShare(user_id=user_id, share_cents=share_cents)
            for user_id, share_cents in shares.items()
        ],
    )


def settlement(payer_id: int, payee_id: int, amount_cents: int) -> Settlement:
    return Settlement(payer_id=payer_id, payee_id=payee_id, amount_cents=amount_cents)


def test_payer_is_owed_what_the_others_consumed() -> None:
    # AC-1: 100.00 split among 4, paid by user 1.
    balances = net_balances(
        member_ids=[1, 2, 3, 4],
        expenses=[expense(payer_id=1, shares={1: 2500, 2: 2500, 3: 2500, 4: 2500})],
        settlements=[],
    )

    assert balances == {1: 7500, 2: -2500, 3: -2500, 4: -2500}


def test_payer_who_did_not_participate_is_owed_the_full_amount() -> None:
    balances = net_balances(
        member_ids=[1, 2], expenses=[expense(payer_id=2, shares={1: 5000})], settlements=[]
    )

    assert balances == {1: -5000, 2: 5000}


def test_balances_accumulate_over_expenses() -> None:
    # AC-4 setup: A owes B 50, B owes C 50 → B is even.
    balances = net_balances(
        member_ids=[1, 2, 3],
        expenses=[expense(payer_id=2, shares={1: 5000}), expense(payer_id=3, shares={2: 5000})],
        settlements=[],
    )

    assert balances == {1: -5000, 2: 0, 3: 5000}


def test_settlement_reduces_debt() -> None:
    # AC-8: B (2) owes A (1) 40.00 and pays it back.
    balances = net_balances(
        member_ids=[1, 2],
        expenses=[expense(payer_id=1, shares={1: 4000, 2: 4000})],
        settlements=[settlement(payer_id=2, payee_id=1, amount_cents=4000)],
    )

    assert balances == {1: 0, 2: 0}


def test_partial_settlement_leaves_the_rest_of_the_debt() -> None:
    balances = net_balances(
        member_ids=[1, 2],
        expenses=[expense(payer_id=1, shares={1: 4000, 2: 4000})],
        settlements=[settlement(payer_id=2, payee_id=1, amount_cents=1500)],
    )

    assert balances == {1: 2500, 2: -2500}


def test_member_without_activity_has_zero_balance() -> None:
    balances = net_balances(member_ids=[1, 2, 3], expenses=[], settlements=[])

    assert balances == {1: 0, 2: 0, 3: 0}


def test_balances_always_sum_to_zero() -> None:
    balances = net_balances(
        member_ids=[1, 2, 3],
        expenses=[
            expense(payer_id=1, shares={1: 3334, 2: 3333, 3: 3333}),
            expense(payer_id=2, shares={1: 1234, 3: 5678}),
        ],
        settlements=[settlement(payer_id=3, payee_id=1, amount_cents=777)],
    )

    assert sum(balances.values()) == 0
