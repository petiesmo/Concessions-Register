#app/db/groups.py
#Database functions for the groups table
#Good template for other types of groups

from sqlmodel import Session
from sqlmodel import select as sqlselect

from app.models.models import Group, GroupShort, GroupCreate, GroupUpdate
from .core import NotFoundError


def create_group(session:Session, group: GroupCreate) -> Group:
    db_group = Group.model_validate(group)
    session.add(db_group)
    session.commit()
    session.refresh(db_group)
    return db_group


def read_groups(session:Session, offset: int=0, limit: int=100):
    groups = session.exec(sqlselect(Group).offset(offset).limit(limit)).all()
    return groups


def read_group(group_id: int, session:Session):
    group = session.get(Group, group_id)
    if not group:
        raise NotFoundError(f"Group {group_id} not found")
    return group


def update_group(session:Session, group_id: int, group: GroupUpdate):
    group_in_db = session.get(Group, group_id)
    if not group_in_db:
        raise NotFoundError(f"Group {group_id} not found")
    group_data = group.model_dump(exclude_unset=True)
    for key, value in group_data.items():
        setattr(group, key, value)
    session.add(group)
    session.commit()
    session.refresh(group)
    return group


def delete_group(session:Session, group_id: int):
    group_in_db = session.get(Group, group_id)
    if not group_in_db:
        raise NotFoundError(f"Group {group_id} not found")
        return False
    session.delete(group_in_db)
    session.commit()
    return True