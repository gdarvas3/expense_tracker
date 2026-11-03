"""Expense schemas. JSON uses "amount"/"percentage"; Python uses *_cents/*_basis_points."""

from datetime import datetime

from pydantic import Field

from app.enums import SplitType
from app.models.expense import DESCRIPTION_MAX_LENGTH
from app.schemas.base import InputSchema, OutputSchema
from app.schemas.fixed_point import HundredthsInput, HundredthsOutput


class ParticipantInput(InputSchema):
    """A participant of an expense; which optional field is required depends on the split type.

    The split-type rules (percentages sum to 100%, exact amounts sum to the total) are
    business rules checked in the service layer, not here.
    """

    user_id: int
    percentage_basis_points: HundredthsInput | None = Field(default=None, alias="percentage")
    share_cents: HundredthsInput | None = Field(default=None, alias="amount")


class ExpenseCreate(InputSchema):
    description: str = Field(min_length=1, max_length=DESCRIPTION_MAX_LENGTH)
    amount_cents: HundredthsInput = Field(alias="amount", gt=0)
    payer_id: int
    split_type: SplitType
    participants: list[ParticipantInput] = Field(min_length=1)


class ShareRead(OutputSchema):
    user_id: int
    share_cents: HundredthsOutput = Field(serialization_alias="amount")
    percentage_basis_points: HundredthsOutput | None = Field(serialization_alias="percentage")


class ExpenseRead(OutputSchema):
    id: int
    description: str
    amount_cents: HundredthsOutput = Field(serialization_alias="amount")
    payer_id: int
    split_type: SplitType
    created_at: datetime
    shares: list[ShareRead]
