"""Expense splitting rules (AC-1, AC-2, AC-3, AC-5) as pure functions."""

from app.enums import SplitType
from app.schemas.expense import ParticipantInput


def calculate_shares(
    amount_cents: int, split_type: SplitType, participants: list[ParticipantInput]
) -> dict[int, int]:
    """Return each participant's share in cents; the shares always sum to the amount.

    Raises:
        ValidationError: If the participants do not describe a valid split of the amount.
    """
    raise NotImplementedError
