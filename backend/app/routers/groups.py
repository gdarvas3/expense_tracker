from fastapi import APIRouter, status

from app.dependencies import CurrentUser, DbSession, GroupAdmin, GroupMember
from app.models import Group, Membership
from app.schemas.group import GroupCreate, GroupRead, MemberAdd, MemberRead
from app.services import group_service

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=GroupRead)
def create_group(body: GroupCreate, user: CurrentUser, db: DbSession) -> Group:
    return group_service.create_group(db, body, user)


@router.get("", response_model=list[GroupRead])
def list_my_groups(user: CurrentUser, db: DbSession) -> list[Group]:
    return group_service.list_groups_of(db, user)


@router.get("/{group_id}", response_model=GroupRead)
def get_group(membership: GroupMember) -> Group:
    return membership.group


@router.post(
    "/{group_id}/members", status_code=status.HTTP_201_CREATED, response_model=MemberRead
)
def add_member(body: MemberAdd, admin: GroupAdmin, db: DbSession) -> Membership:
    return group_service.add_member(db, admin.group, body.user_id)


@router.delete("/{group_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(user_id: int, admin: GroupAdmin, db: DbSession) -> None:
    group_service.remove_member(db, admin.group, user_id)
