"""Request dependencies: who is calling, and may they access the group."""

from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.enums import MemberRole
from app.exceptions import ForbiddenError, NotFoundError, UnauthorizedError
from app.models import Group, Membership, User

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(db: DbSession, x_user_id: Annotated[str | None, Header()] = None) -> User:
    """Identify the caller from the X-User-Id header.

    Raises:
        UnauthorizedError: If the header is missing, not a positive integer, or unknown.
    """
    user = db.get(User, parse_user_id(x_user_id))
    if user is None:
        raise UnauthorizedError("Unknown user.")
    return user


def parse_user_id(header_value: str | None) -> int:
    # isascii() guards against Unicode digits such as "²", which isdigit() accepts.
    if not header_value or not (header_value.isascii() and header_value.isdigit()):
        raise UnauthorizedError("Missing or invalid X-User-Id header.")
    return int(header_value)


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_group_member(group_id: int, user: CurrentUser, db: DbSession) -> Membership:
    """Return the caller's membership in the group.

    Raises:
        NotFoundError: If the group does not exist.
        ForbiddenError: If the caller is not a member (AC-7).
    """
    if db.get(Group, group_id) is None:
        raise NotFoundError("Group not found.")
    membership = db.get(Membership, (group_id, user.id))
    if membership is None:
        raise ForbiddenError("You are not a member of this group.")
    return membership


GroupMember = Annotated[Membership, Depends(require_group_member)]


def require_group_admin(membership: GroupMember) -> Membership:
    """Return the caller's membership if they are the group admin.

    Raises:
        ForbiddenError: If the caller is a regular member.
    """
    if membership.role is not MemberRole.ADMIN:
        raise ForbiddenError("Only the group admin can do this.")
    return membership


GroupAdmin = Annotated[Membership, Depends(require_group_admin)]
