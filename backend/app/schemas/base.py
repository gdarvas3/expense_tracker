from pydantic import BaseModel, ConfigDict


class InputSchema(BaseModel):
    """Base for request bodies: unknown fields are rejected instead of silently ignored."""

    model_config = ConfigDict(extra="forbid")


class OutputSchema(BaseModel):
    """Base for responses: can be built directly from ORM objects."""

    model_config = ConfigDict(from_attributes=True)
