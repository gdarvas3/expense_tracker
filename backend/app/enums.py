"""Enumerations shared by ORM models and API schemas."""

from enum import StrEnum


class MemberRole(StrEnum):
    ADMIN = "admin"
    MEMBER = "member"


class SplitType(StrEnum):
    EQUAL = "equal"
    PERCENTAGE = "percentage"
    EXACT = "exact"
