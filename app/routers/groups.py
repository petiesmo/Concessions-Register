#router/groups.py
#Defines API functions at the endpoints
#Good template: Can be replicated and adjusted for other group types.
#Many ideas from: https://github.com/ArjanCodes/examples/blob/main/2023/fastapi-router/
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.models.models import Group, GroupShort, GroupCreate, GroupUpdate
import app.db.core as db_core
import app.db.groups as db
from .limiter import limiter


router = APIRouter(
    prefix='/groups',
    tags=['groups'],
    dependencies=[],
    responses={404: {'description': 'Not found'}}
)

#-- CREATE
@router.post("/", response_model=GroupShort)
@limiter.limit("1/second")
def create_group(group: GroupCreate, session:Session = Depends(db_core.get_session)):
    try:
        db.create_group(session, group)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group not created")
    return group


#-- READ
@router.get("/", response_model=List[GroupShort])
@limiter.limit("1/second")
def read_groups(offset: int=0, limit: int=Query(default=100, le=100), session:Session = Depends(db_core.get_session)):
    groups = db.read_groups(session, offset, limit)
    return groups

@router.get("/{group_id}", response_model=GroupShort)
@limiter.limit("1/second")
def read_group(group_id: int, session:Session = Depends(db_core.get_session)):
    group = session.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return group


#-- UPDATE
@router.patch("/{group_id}", response_model=GroupShort)
@limiter.limit("1/second")
def update_group(group_id: int, group: GroupUpdate, session:Session = Depends(db_core.get_session)):
    try:
        updated_group = db.update_group(session, group_id, group)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group not updated")
    return updated_group


#-- DELETE
@router.delete("/{group_id}")
@limiter.limit("1/second")
def delete_group(group_id: int, session:Session = Depends(db_core.get_session)):
    try:
        db.delete_group(session, group_id)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group not updated")
    return {'ok': f'deleted Group {group_id}'}