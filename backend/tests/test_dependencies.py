"""Tests for request dependencies: caller identification and group access guards."""

import pytest
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, require_group_admin, require_group_member
from app.enums import MemberRole
from app.exceptions import ForbiddenError, NotFoundError, UnauthorizedError
from app.models import Group, Membership, User


@pytest.fixture
def admin(db_session: Session) -> User:
    return add_user(db_session, "Alice")


@pytest.fixture
def member(db_session: Session) -> User:
    return add_user(db_session, "Bob")


@pytest.fixture
def outsider(db_session: Session) -> User:
    return add_user(db_session, "Mallory")


@pytest.fixture
def group(db_session: Session, admin: User, member: User) -> Group:
    group = Group(
        name="Trip",
        memberships=[
            Membership(user=admin, role=MemberRole.ADMIN),
            Membership(user=member, role=MemberRole.MEMBER),
        ],
    )
    db_session.add(group)
    db_session.commit()
    return group


def add_user(db_session: Session, name: str) -> User:
    user = User(name=name)
    db_session.add(user)
    db_session.commit()
    return user


def test_current_user_is_resolved_from_header(db_session: Session, admin: User) -> None:
    assert get_current_user(db=db_session, x_user_id=str(admin.id)) is admin


@pytest.mark.parametrize("header_value", [None, "", "abc", "-1", "1.5", "999"])
def test_missing_invalid_or_unknown_user_id_is_unauthorized(
    db_session: Session, header_value: str | None
) -> None:
    with pytest.raises(UnauthorizedError):
        get_current_user(db=db_session, x_user_id=header_value)


def test_group_member_gets_their_membership(
    db_session: Session, group: Group, member: User
) -> None:
    membership = require_group_member(group_id=group.id, user=member, db=db_session)

    assert membership.user is member
    assert membership.role is MemberRole.MEMBER


def test_non_member_is_forbidden(db_session: Session, group: Group, outsider: User) -> None:
    # AC-7: non-members cannot view or modify group data.
    with pytest.raises(ForbiddenError):
        require_group_member(group_id=group.id, user=outsider, db=db_session)


def test_unknown_group_is_not_found(db_session: Session, admin: User) -> None:
    with pytest.raises(NotFoundError):
        require_group_member(group_id=999, user=admin, db=db_session)


def test_admin_passes_admin_guard(db_session: Session, group: Group, admin: User) -> None:
    membership = require_group_member(group_id=group.id, user=admin, db=db_session)

    assert require_group_admin(membership) is membership


def test_regular_member_fails_admin_guard(
    db_session: Session, group: Group, member: User
) -> None:
    membership = require_group_member(group_id=group.id, user=member, db=db_session)

    with pytest.raises(ForbiddenError):
        require_group_admin(membership)
