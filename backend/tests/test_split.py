"""Unit tests for the splitting rules: equal, percentage and exact splits in integer cents."""

import pytest

from app.enums import SplitType
from app.exceptions import ValidationError
from app.schemas.expense import ParticipantInput
from app.services.split import calculate_shares


def plain(*user_ids: int) -> list[ParticipantInput]:
    return [ParticipantInput.model_validate({"user_id": user_id}) for user_id in user_ids]


def with_percentages(percentages: dict[int, str]) -> list[ParticipantInput]:
    return [
        ParticipantInput.model_validate({"user_id": user_id, "percentage": percentage})
        for user_id, percentage in percentages.items()
    ]


def with_amounts(amounts: dict[int, str]) -> list[ParticipantInput]:
    return [
        ParticipantInput.model_validate({"user_id": user_id, "amount": amount})
        for user_id, amount in amounts.items()
    ]


def test_equal_split_without_remainder() -> None:
    shares = calculate_shares(10000, SplitType.EQUAL, plain(1, 2, 3, 4))

    assert shares == {1: 2500, 2: 2500, 3: 2500, 4: 2500}


def test_equal_split_gives_leftover_cent_to_lowest_user_id() -> None:
    # AC-3, with the participants deliberately out of order.
    shares = calculate_shares(10000, SplitType.EQUAL, plain(3, 1, 2))

    assert shares == {1: 3334, 2: 3333, 3: 3333}


def test_equal_split_sorts_user_ids_numerically() -> None:
    shares = calculate_shares(3, SplitType.EQUAL, plain(10, 9))

    assert shares == {9: 2, 10: 1}


def test_equal_split_of_fewer_cents_than_participants() -> None:
    shares = calculate_shares(2, SplitType.EQUAL, plain(1, 2, 3))

    assert shares == {1: 1, 2: 1, 3: 0}


@pytest.mark.parametrize("amount_cents", [1, 99, 100, 10001, 123457])
@pytest.mark.parametrize("participant_count", [1, 3, 7])
def test_equal_shares_always_sum_to_amount(amount_cents: int, participant_count: int) -> None:
    participants = plain(*range(1, participant_count + 1))

    shares = calculate_shares(amount_cents, SplitType.EQUAL, participants)

    assert sum(shares.values()) == amount_cents
    assert max(shares.values()) - min(shares.values()) <= 1


def test_percentage_split() -> None:
    # AC-2
    shares = calculate_shares(
        20000, SplitType.PERCENTAGE, with_percentages({1: "50", 2: "30", 3: "20"})
    )

    assert shares == {1: 10000, 2: 6000, 3: 4000}


def test_percentage_split_gives_leftover_cent_to_lowest_user_id() -> None:
    # 10.00 × 33.33% = 3.333 → 3.33 each; the lost cent goes to user 1.
    shares = calculate_shares(
        1000, SplitType.PERCENTAGE, with_percentages({3: "33.34", 2: "33.33", 1: "33.33"})
    )

    assert shares == {1: 334, 2: 333, 3: 333}
    assert sum(shares.values()) == 1000


def test_exact_split() -> None:
    shares = calculate_shares(10000, SplitType.EXACT, with_amounts({1: "70.00", 2: "30.00"}))

    assert shares == {1: 7000, 2: 3000}


@pytest.mark.parametrize(
    ("split_type", "participants"),
    [
        pytest.param(
            SplitType.PERCENTAGE, with_percentages({1: "50", 2: "40"}), id="percent-below-100"
        ),
        pytest.param(
            SplitType.PERCENTAGE, with_percentages({1: "60", 2: "50"}), id="percent-above-100"
        ),
        pytest.param(
            SplitType.PERCENTAGE, with_percentages({1: "110", 2: "-10"}), id="percent-negative"
        ),
        pytest.param(SplitType.PERCENTAGE, plain(1, 2), id="percent-missing"),
        pytest.param(
            SplitType.PERCENTAGE, with_amounts({1: "50.00", 2: "50.00"}), id="percent-got-amounts"
        ),
        pytest.param(
            SplitType.EXACT, with_amounts({1: "30.00", 2: "60.00"}), id="exact-below-total"
        ),
        pytest.param(
            SplitType.EXACT, with_amounts({1: "50.00", 2: "50.01"}), id="exact-above-total"
        ),
        pytest.param(
            SplitType.EXACT, with_amounts({1: "110.00", 2: "-10.00"}), id="exact-negative"
        ),
        pytest.param(SplitType.EXACT, plain(1, 2), id="exact-missing"),
        pytest.param(
            SplitType.EXACT, with_percentages({1: "50", 2: "50"}), id="exact-got-percentages"
        ),
        pytest.param(
            SplitType.EQUAL, with_amounts({1: "50.00", 2: "50.00"}), id="equal-got-amounts"
        ),
        pytest.param(
            SplitType.EQUAL, with_percentages({1: "50", 2: "50"}), id="equal-got-percentages"
        ),
    ],
)
def test_invalid_split_is_rejected(
    split_type: SplitType, participants: list[ParticipantInput]
) -> None:
    # AC-5
    with pytest.raises(ValidationError):
        calculate_shares(10000, split_type, participants)
