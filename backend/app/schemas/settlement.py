from datetime import datetime

from pydantic import Field

from app.schemas.base import InputSchema, OutputSchema
from app.schemas.fixed_point import HundredthsInput, HundredthsOutput


class SettlementCreate(InputSchema):
    payer_id: int
    payee_id: int
    amount_cents: HundredthsInput = Field(alias="amount", gt=0)


class SettlementRead(OutputSchema):
    id: int
    payer_id: int
    payee_id: int
    amount_cents: HundredthsOutput = Field(serialization_alias="amount")
    created_at: datetime
