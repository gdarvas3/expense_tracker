from datetime import datetime

from pydantic import Field

from app.enums import MemberRole
from app.models.group import GROUP_NAME_MAX_LENGTH
from app.schemas.base import InputSchema, OutputSchema


class GroupCreate(InputSchema):
    name: str = Field(min_length=1, max_length=GROUP_NAME_MAX_LENGTH)


class MemberAdd(InputSchema):
    user_id: int


class MemberRead(OutputSchema):
    user_id: int
    role: MemberRole


class GroupRead(OutputSchema):
    id: int
    name: str
    created_at: datetime
    members: list[MemberRead] = Field(validation_alias="memberships")
