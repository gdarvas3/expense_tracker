from pydantic import Field

from app.schemas.base import OutputSchema
from app.schemas.fixed_point import HundredthsOutput


class BalanceRead(OutputSchema):
    """Net balance of a member: positive means the others owe them."""

    user_id: int
    net_cents: HundredthsOutput = Field(serialization_alias="net")


class TransferRead(OutputSchema):
    """One payment of the simplified settlement plan (AC-4)."""

    from_user_id: int
    to_user_id: int
    amount_cents: HundredthsOutput = Field(serialization_alias="amount")
