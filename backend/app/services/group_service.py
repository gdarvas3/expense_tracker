from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enums import MemberRole
from app.exceptions import ConflictError, NotFoundError
from app.models import Group, Membership, User
from app.schemas.group import GroupCreate
from app.services.balance_service import calculate_balances
from app.services.membership import member_ids


def create_group(db: Session, data: GroupCreate, creator: User) -> Group:
    """Create a group; the creator becomes its admin."""
    group = Group(name=data.name, memberships=[Membership(user=creator, role=MemberRole.ADMIN)])
    db.add(group)
    db.commit()
    return group


def list_groups_of(db: Session, user: User) -> list[Group]:
    query = select(Group).join(Membership).where(Membership.user_id == user.id).order_by(Group.id)
    return list(db.scalars(query))


def add_member(db: Session, group: Group, user_id: int) -> Membership:
    """Add an existing user to the group as a regular member.

    Raises:
        NotFoundError: If the user does not exist.
        ConflictError: If the user is already a member.
    """
    if db.get(User, user_id) is None:
        raise NotFoundError("User not found.")
    if user_id in member_ids(group):
        raise ConflictError("User is already a member of this group.")
    membership = Membership(group=group, user_id=user_id, role=MemberRole.MEMBER)
    db.add(membership)
    db.commit()
    return membership


def remove_member(db: Session, group: Group, user_id: int) -> None:
    """Remove a member whose net balance is exactly zero.

    Raises:
        NotFoundError: If the user is not a member of the group.
        ConflictError: If the member still owes or is owed money (AC-6).
    """
    membership = db.get(Membership, (group.id, user_id))
    if membership is None:
        raise NotFoundError("User is not a member of this group.")
    if calculate_balances(db, group).get(user_id, 0) != 0:
        raise ConflictError("Only members with a zero balance can be removed.")
    db.delete(membership)
    db.commit()

