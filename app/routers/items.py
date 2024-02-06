#router/items.py
#Defines API functions at the endpoints
#Good template: Can be replicated and adjusted for other item types.
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.models.item import Item, ItemShort, ItemCreate, ItemUpdate
import app.db.core as db
import app.db.items as db_items


router = APIRouter(
    prefix='/items',
    tags=['items'],
    dependencies=[],
    responses={404: {'description': 'Not found'}}
)

#-- CREATE
@router.post("/", response_model=ItemShort)
def create_item(item: ItemCreate, session:Session = Depends(db.get_session)):
    try:
        db_items.create_item(session, item)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Item not created")
    return item


#-- READ
@router.get("/", response_model=List[ItemShort])
def read_items(offset: int=0, limit: int=Query(default=100, le=100), session:Session = Depends(db.get_session)):
    items = db_items.read_items(session, offset, limit)
    return items

@router.get("/{item_id}", response_model=ItemShort)
def read_item(item_id: int, session:Session = Depends(db.get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


#-- UPDATE
@router.patch("/{item_id}", response_model=ItemShort)
def update_item(item_id: int, item: ItemUpdate, session:Session = Depends(db.get_session)):
    try:
        updated_item = db_items.update_item(session, item_id, item)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Item not updated")
    return updated_item


#-- DELETE
@router.delete("/{item_id}")
def delete_item(item_id: int, session:Session = Depends(db.get_session)):
    try:
        db_items.delete_item(session, item_id)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Item not updated")
    return {'ok': f'deleted Item {item_id}'}