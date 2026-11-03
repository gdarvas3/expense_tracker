"""Acceptance tests: end-to-end API tests for each acceptance criterion (AC-1 … AC-8)."""

from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient

from api_client import ExpenseApi, as_user

ExpenseBuilder = Callable[[int, int], dict[str, object]]


def equal_expense(payer_id: int, amount: str, participant_ids: list[int]) -> dict[str, object]:
    return {
        "description": "Shared expense",
        "amount": amount,
        "payer_id": payer_id,
        "split_type": "equal",
        "participants": [{"user_id": user_id} for user_id in participant_ids],
    }


def exact_expense(payer_id: int, amount: str, shares: dict[int, str]) -> dict[str, object]:
    return {
        "description": "Shared expense",
        "amount": amount,
        "payer_id": payer_id,
        "split_type": "exact",
        "participants": [
            {"user_id": user_id, "amount": share} for user_id, share in shares.items()
        ],
    }


def percentage_expense(
    payer_id: int, amount: str, percentages: dict[int, str]
) -> dict[str, object]:
    return {
        "description": "Shared expense",
        "amount": amount,
        "payer_id": payer_id,
        "split_type": "percentage",
        "participants": [
            {"user_id": user_id, "percentage": percentage}
            for user_id, percentage in percentages.items()
        ],
    }


def shares_by_user(expense: dict[str, object]) -> dict[int, str]:
    return {share["user_id"]: share["amount"] for share in expense["shares"]}


def test_ac1_equal_split_gives_each_member_a_quarter(api: ExpenseApi) -> None:
    a, b, c, d = api.create_users("A", "B", "C", "D").values()
    group_id = api.create_group(admin_id=a, member_ids=[b, c, d])

    response = api.add_expense(group_id, a, equal_expense(a, "100.00", [a, b, c, d]))

    assert response.status_code == 201, response.text
    assert shares_by_user(response.json()) == {a: "25.00", b: "25.00", c: "25.00", d: "25.00"}
    assert api.balances(group_id, a) == {a: "75.00", b: "-25.00", c: "-25.00", d: "-25.00"}


def test_ac2_percentage_split_follows_the_given_percentages(api: ExpenseApi) -> None:
    a, b, c = api.create_users("A", "B", "C").values()
    group_id = api.create_group(admin_id=a, member_ids=[b, c])

    response = api.add_expense(
        group_id, a, percentage_expense(a, "200.00", {a: "50", b: "30", c: "20"})
    )

    assert response.status_code == 201, response.text
    assert shares_by_user(response.json()) == {a: "100.00", b: "60.00", c: "40.00"}
    assert api.balances(group_id, a) == {a: "100.00", b: "-60.00", c: "-40.00"}


def test_ac3_leftover_cent_goes_to_the_lowest_user_id(api: ExpenseApi) -> None:
    a, b, c = api.create_users("A", "B", "C").values()
    group_id = api.create_group(admin_id=a, member_ids=[b, c])

    # Participants deliberately listed in reverse: the order of the request must not matter.
    response = api.add_expense(group_id, a, equal_expense(a, "100.00", [c, b, a]))

    assert response.status_code == 201, response.text
    assert shares_by_user(response.json()) == {a: "33.34", b: "33.33", c: "33.33"}
    assert api.balances(group_id, a) == {a: "66.66", b: "-33.33", c: "-33.33"}


def test_ac3_leftover_cents_follow_numeric_user_id_order(api: ExpenseApi) -> None:
    # Interpretation of "alphabetically by user ID": IDs sort numerically, so 9 before 10.
    user_ids = [api.create_user(f"User {number}") for number in range(1, 11)]
    user_9, user_10 = user_ids[8], user_ids[9]
    assert (user_9, user_10) == (9, 10)
    group_id = api.create_group(admin_id=user_10, member_ids=[user_9])

    response = api.add_expense(
        group_id, user_10, equal_expense(user_10, "0.03", [user_10, user_9])
    )

    assert response.status_code == 201, response.text
    assert shares_by_user(response.json()) == {user_9: "0.02", user_10: "0.01"}


def test_ac4_transitive_debt_becomes_a_single_payment(api: ExpenseApi) -> None:
    a, b, c = api.create_users("A", "B", "C").values()
    group_id = api.create_group(admin_id=a, member_ids=[b, c])
    api.add_expense(group_id, b, exact_expense(b, "50.00", {a: "50.00"}))  # A owes B 50
    api.add_expense(group_id, c, exact_expense(c, "50.00", {b: "50.00"}))  # B owes C 50

    plan = api.settlement_plan(group_id, a)

    assert plan == [{"from_user_id": a, "to_user_id": c, "amount": "50.00"}]


def zero_amount(payer_id: int, other_id: int) -> dict[str, object]:
    return equal_expense(payer_id, "0.00", [payer_id, other_id])


def negative_amount(payer_id: int, other_id: int) -> dict[str, object]:
    return equal_expense(payer_id, "-10.00", [payer_id, other_id])


def percentages_below_100(payer_id: int, other_id: int) -> dict[str, object]:
    return percentage_expense(payer_id, "100.00", {payer_id: "50", other_id: "40"})


def percentages_above_100(payer_id: int, other_id: int) -> dict[str, object]:
    return percentage_expense(payer_id, "100.00", {payer_id: "60", other_id: "50"})


def exact_shares_below_total(payer_id: int, other_id: int) -> dict[str, object]:
    return exact_expense(payer_id, "100.00", {payer_id: "30.00", other_id: "60.00"})


def exact_shares_above_total(payer_id: int, other_id: int) -> dict[str, object]:
    return exact_expense(payer_id, "100.00", {payer_id: "50.00", other_id: "50.01"})


@pytest.mark.parametrize(
    "build_invalid_expense",
    [
        zero_amount,
        negative_amount,
        percentages_below_100,
        percentages_above_100,
        exact_shares_below_total,
        exact_shares_above_total,
    ],
    ids=[
        "amount-zero",
        "amount-negative",
        "percentages-below-100",
        "percentages-above-100",
        "exact-sum-below-total",
        "exact-sum-above-total",
    ],
)
def test_ac5_invalid_split_is_rejected_with_400(
    api: ExpenseApi, build_invalid_expense: ExpenseBuilder
) -> None:
    a, b = api.create_users("A", "B").values()
    group_id = api.create_group(admin_id=a, member_ids=[b])

    response = api.add_expense(group_id, a, build_invalid_expense(a, b))

    assert response.status_code == 400, response.text
    assert api.list_expenses(group_id, a) == []


def test_ac6_member_with_balance_cannot_be_removed(api: ExpenseApi) -> None:
    a, b = api.create_users("A", "B").values()
    group_id = api.create_group(admin_id=a, member_ids=[b])
    api.add_expense(group_id, a, equal_expense(a, "30.00", [a, b]))
    assert api.balances(group_id, a)[b] == "-15.00"

    response = api.remove_member(group_id, admin_id=a, member_id=b)

    assert response.status_code == 409, response.text
    assert b in api.member_ids(group_id, a)


def test_ac6_member_with_zero_balance_can_be_removed(api: ExpenseApi) -> None:
    a, b, c = api.create_users("A", "B", "C").values()
    group_id = api.create_group(admin_id=a, member_ids=[b, c])
    api.add_expense(group_id, a, equal_expense(a, "30.00", [a, b]))

    response = api.remove_member(group_id, admin_id=a, member_id=c)

    assert response.status_code == 204, response.text
    assert c not in api.member_ids(group_id, a)


@pytest.mark.parametrize(
    ("method", "path_suffix"),
    [
        ("GET", ""),
        ("GET", "/expenses"),
        ("POST", "/expenses"),
        ("GET", "/balances"),
        ("GET", "/settlement-plan"),
        ("POST", "/settlements"),
        ("POST", "/members"),
        ("DELETE", "/members/1"),
    ],
)
def test_ac7_non_member_is_rejected_with_403(
    api: ExpenseApi, client: TestClient, method: str, path_suffix: str
) -> None:
    admin, outsider = api.create_users("Admin", "Outsider").values()
    group_id = api.create_group(admin_id=admin, member_ids=[])
    # Valid bodies, so a 403 cannot be confused with a 400 from body validation.
    valid_bodies: dict[str, dict[str, object]] = {
        "/expenses": equal_expense(outsider, "10.00", [outsider]),
        "/settlements": {"payer_id": outsider, "payee_id": admin, "amount": "10.00"},
        "/members": {"user_id": outsider},
    }
    body = valid_bodies.get(path_suffix) if method == "POST" else None

    response = client.request(
        method, f"/api/groups/{group_id}{path_suffix}", json=body, headers=as_user(outsider)
    )

    assert response.status_code == 403, response.text


def test_ac8_settlement_brings_balances_to_zero(api: ExpenseApi) -> None:
    a, b = api.create_users("A", "B").values()
    group_id = api.create_group(admin_id=a, member_ids=[b])
    api.add_expense(group_id, a, equal_expense(a, "80.00", [a, b]))
    assert api.balances(group_id, a) == {a: "40.00", b: "-40.00"}  # B owes A 40

    response = api.record_settlement(
        group_id, b, {"payer_id": b, "payee_id": a, "amount": "40.00"}
    )

    assert response.status_code == 201, response.text
    assert api.balances(group_id, a) == {a: "0.00", b: "0.00"}
    assert api.settlement_plan(group_id, a) == []
