from pydantic import Field

from app.models.user import NAME_MAX_LENGTH
from app.schemas.base import InputSchema, OutputSchema


class UserCreate(InputSchema):
    name: str = Field(min_length=1, max_length=NAME_MAX_LENGTH)


class UserRead(OutputSchema):
    id: int
    name: str
