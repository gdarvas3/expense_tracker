from dataclasses import dataclass


@dataclass(frozen=True)
class Transfer:
    """One payment of a settlement plan."""

    from_user_id: int
    to_user_id: int
    amount_cents: int
