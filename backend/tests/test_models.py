"""Tests for ORM models: relationships and database-level integrity constraints."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.enums import MemberRole, SplitType
from app.models import Expense, ExpenseShare, Group, Membership, Settlement, User


@pytest.fixture
def group_with_two_members(db_session: Session) -> Group:
    alice = User(name="Alice")
    bob = User(name="Bob")
    group = Group(
        name="Flat 4B",
        memberships=[
            Membership(user=alice, role=MemberRole.ADMIN),
            Membership(user=bob, role=MemberRole.MEMBER),
        ],
    )
    db_session.add(group)
    db_session.commit()
    return group


def test_expense_is_stored_with_its_shares(
    db_session: Session, group_with_two_members: Group
) -> None:
    alice, bob = (membership.user for membership in group_with_two_members.memberships)
    expense = Expense(
        group=group_with_two_members,
        payer=alice,
        description="Dinner",
        amount_cents=10000,
        split_type=SplitType.EQUAL,
        shares=[
            ExpenseShare(user=alice, share_cents=5000),
            ExpenseShare(user=bob, share_cents=5000),
        ],
    )
    db_session.add(expense)
    db_session.commit()

    stored = db_session.get(Expense, expense.id)
    assert stored is not None
    assert stored.created_at is not None
    assert sorted(share.share_cents for share in stored.shares) == [5000, 5000]


def test_expense_amount_must_be_positive(
    db_session: Session, group_with_two_members: Group
) -> None:
    alice = group_with_two_members.memberships[0].user
    db_session.add(
        Expense(
            group=group_with_two_members,
            payer=alice,
            description="Nothing",
            amount_cents=0,
            split_type=SplitType.EQUAL,
        )
    )

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_settlement_payer_and_payee_must_differ(
    db_session: Session, group_with_two_members: Group
) -> None:
    alice = group_with_two_members.memberships[0].user
    db_session.add(
        Settlement(group=group_with_two_members, payer=alice, payee=alice, amount_cents=100)
    )

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_user_can_be_member_of_a_group_only_once(
    db_session: Session, group_with_two_members: Group
) -> None:
    alice = group_with_two_members.memberships[0].user
    db_session.add(Membership(group=group_with_two_members, user=alice, role=MemberRole.MEMBER))

    with pytest.raises(IntegrityError):
        db_session.commit()
