"""Membership helpers shared by the group, expense, settlement and balance services."""

from collections.abc import Iterable

from app.exceptions import ValidationError
from app.models import Group


def member_ids(group: Group) -> set[int]:
    return {membership.user_id for membership in group.memberships}


def ensure_members(group: Group, user_ids: Iterable[int]) -> None:
    """Raise if any user ID does not belong to the group.

    Raises:
        ValidationError: If a user is not a member; such input is invalid, not forbidden.
    """
    outsiders = set(user_ids) - member_ids(group)
    if outsiders:
        raise ValidationError(f"Users are not members of this group: {sorted(outsiders)}.")
