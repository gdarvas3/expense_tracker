"""Tests for debt simplification (AC-4), run against every AI-written implementation.

To compare a new variant, add it to IMPLEMENTATIONS; every test then runs for it too.
"""

from collections.abc import Callable

import pytest

from app.services.settlement import Transfer, claude_code

SimplifyDebts = Callable[[dict[int, int]], list[Transfer]]

IMPLEMENTATIONS = [
    pytest.param(claude_code.simplify_debts, id="claude_code"),
]


@pytest.fixture(params=IMPLEMENTATIONS)
def simplify_debts(request: pytest.FixtureRequest) -> SimplifyDebts:
    return request.param


def apply_transfers(balances: dict[int, int], transfers: list[Transfer]) -> dict[int, int]:
    remaining = dict(balances)
    for transfer in transfers:
        remaining[transfer.from_user_id] += transfer.amount_cents
        remaining[transfer.to_user_id] -= transfer.amount_cents
    return remaining


def test_transitive_debt_becomes_one_transfer(simplify_debts: SimplifyDebts) -> None:
    # AC-4: A (1) owes B (2) 50, B owes C (3) 50 → B nets to zero.
    transfers = simplify_debts({1: -5000, 2: 0, 3: 5000})

    assert transfers == [Transfer(from_user_id=1, to_user_id=3, amount_cents=5000)]


@pytest.mark.parametrize("balances", [{}, {1: 0, 2: 0}], ids=["no-members", "all-settled"])
def test_settled_group_needs_no_transfers(
    simplify_debts: SimplifyDebts, balances: dict[int, int]
) -> None:
    assert simplify_debts(balances) == []


def test_one_debtor_pays_creditors_largest_first(simplify_debts: SimplifyDebts) -> None:
    transfers = simplify_debts({1: -9000, 2: 4000, 3: 5000})

    assert transfers == [Transfer(1, 3, 5000), Transfer(1, 2, 4000)]


def test_equal_debtors_pay_in_ascending_user_id_order(simplify_debts: SimplifyDebts) -> None:
    # AC-1 balances: three members owe the payer 25.00 each.
    transfers = simplify_debts({1: 7500, 2: -2500, 3: -2500, 4: -2500})

    assert transfers == [Transfer(2, 1, 2500), Transfer(3, 1, 2500), Transfer(4, 1, 2500)]


def test_greedy_always_matches_current_largest_debtor_and_creditor(
    simplify_debts: SimplifyDebts,
) -> None:
    # Round 1: 1 (-60) → 3 (+70) 60.  Round 2: 2 (-40) → 4 (+30) 30.  Round 3: 2 (-10) → 3 (+10).
    transfers = simplify_debts({1: -6000, 2: -4000, 3: 7000, 4: 3000})

    assert transfers == [Transfer(1, 3, 6000), Transfer(2, 4, 3000), Transfer(2, 3, 1000)]


@pytest.mark.parametrize(
    "balances",
    [
        {1: 7500, 2: -2500, 3: -2500, 4: -2500},
        {1: -1, 2: -1, 3: 2},
        {1: 12345, 2: -6789, 3: -5556, 4: 0, 5: 3000, 6: -3000},
        {user_id: (user_id % 5 - 2) * 101 for user_id in range(1, 21)},
    ],
)
def test_transfers_settle_every_balance(
    simplify_debts: SimplifyDebts, balances: dict[int, int]
) -> None:
    transfers = simplify_debts(balances)

    assert all(net == 0 for net in apply_transfers(balances, transfers).values())
    assert all(transfer.amount_cents > 0 for transfer in transfers)
    open_balance_count = sum(1 for net in balances.values() if net != 0)
    assert len(transfers) <= max(open_balance_count - 1, 0)


def test_input_balances_are_not_modified(simplify_debts: SimplifyDebts) -> None:
    balances = {1: -5000, 2: 5000}

    simplify_debts(balances)

    assert balances == {1: -5000, 2: 5000}


def test_unbalanced_input_is_rejected(simplify_debts: SimplifyDebts) -> None:
    with pytest.raises(ValueError):
        simplify_debts({1: -5000, 2: 4000})
