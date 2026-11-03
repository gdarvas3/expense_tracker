"""Expense splitting rules (AC-1, AC-2, AC-3, AC-5) as pure functions on integer cents."""

from collections.abc import Callable
from operator import attrgetter

from app.enums import SplitType
from app.exceptions import ValidationError
from app.schemas.expense import ParticipantInput

FULL_PERCENT_BASIS_POINTS = 10_000

ParticipantValue = Callable[[ParticipantInput], int | None]
get_percentage = attrgetter("percentage_basis_points")
get_exact_amount = attrgetter("share_cents")


def calculate_shares(
    amount_cents: int, split_type: SplitType, participants: list[ParticipantInput]
) -> dict[int, int]:
    """Return each participant's share in cents; the shares always sum to the amount.

    Raises:
        ValidationError: If the participants do not describe a valid split of the amount.
    """
    split = SPLITTERS_BY_TYPE[split_type]
    return split(amount_cents, participants)


def split_equally(amount_cents: int, participants: list[ParticipantInput]) -> dict[int, int]:
    ensure_not_given(participants, get_percentage, "percentage")
    ensure_not_given(participants, get_exact_amount, "amount")
    base_share, leftover_cents = divmod(amount_cents, len(participants))
    base_shares = {participant.user_id: base_share for participant in participants}
    return give_leftover_cents(base_shares, leftover_cents)


def split_by_percentage(
    amount_cents: int, participants: list[ParticipantInput]
) -> dict[int, int]:
    ensure_not_given(participants, get_exact_amount, "amount")
    percentages = required_values(participants, get_percentage, "percentage")
    if sum(percentages.values()) != FULL_PERCENT_BASIS_POINTS:
        raise ValidationError("Percentages must add up to exactly 100%.")
    # Floor each share; the cents lost to flooring are handed out by the remainder rule.
    base_shares = {
        user_id: amount_cents * basis_points // FULL_PERCENT_BASIS_POINTS
        for user_id, basis_points in percentages.items()
    }
    return give_leftover_cents(base_shares, amount_cents - sum(base_shares.values()))


def split_exactly(amount_cents: int, participants: list[ParticipantInput]) -> dict[int, int]:
    ensure_not_given(participants, get_percentage, "percentage")
    shares = required_values(participants, get_exact_amount, "amount")
    if sum(shares.values()) != amount_cents:
        raise ValidationError("Exact shares must add up to the expense amount.")
    return shares


def give_leftover_cents(base_shares: dict[int, int], leftover_cents: int) -> dict[int, int]:
    """Add one cent each to the first participants by ascending user ID (spec remainder rule)."""
    shares = dict(base_shares)
    for user_id in sorted(shares)[:leftover_cents]:
        shares[user_id] += 1
    return shares


def required_values(
    participants: list[ParticipantInput], get_value: ParticipantValue, field_name: str
) -> dict[int, int]:
    """Collect a non-negative value from every participant, keyed by user ID.

    Raises:
        ValidationError: If a participant lacks the value or it is negative.
    """
    values: dict[int, int] = {}
    for participant in participants:
        value = get_value(participant)
        if value is None:
            raise ValidationError(f"Every participant needs a '{field_name}'.")
        if value < 0:
            raise ValidationError(f"'{field_name}' cannot be negative.")
        values[participant.user_id] = value
    return values


def ensure_not_given(
    participants: list[ParticipantInput], get_value: ParticipantValue, field_name: str
) -> None:
    """Reject values that the split type ignores, so a request cannot be silently misread."""
    if any(get_value(participant) is not None for participant in participants):
        raise ValidationError(f"'{field_name}' is not allowed for this split type.")


SPLITTERS_BY_TYPE: dict[SplitType, Callable[[int, list[ParticipantInput]], dict[int, int]]] = {
    SplitType.EQUAL: split_equally,
    SplitType.PERCENTAGE: split_by_percentage,
    SplitType.EXACT: split_exactly,
}
