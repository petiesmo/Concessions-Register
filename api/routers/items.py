#router/items.py
#Defines API functions at the endpoints
#Good template: Can be replicated and adjusted for other item types.
#Many ideas from: https://github.com/ArjanCodes/examples/blob/main/2023/fastapi-router/
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from api.models.models import Item, ItemShort, ItemCreate, ItemUpdate
import api.db.core as db_core
import api.db.items as db


router = APIRouter(
    prefix='/items',
    tags=['items'],
    dependencies=[],
    responses={404: {'description': 'Not found'}}
)

@router.get("/", response_model=form.Item)
async def return_html_form():
    basic_screen = "<html><body><h1>The Most Basic items ever</h1></body></html>"
    return basic_screen


#-- CREATE
@router.post("/", response_model=ItemShort)
def create_item(item: ItemCreate, session:Session = Depends(db_core.get_session)):
    try:
        db.create_item(session, item)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Item not created")
    return item


#-- READ
@router.get("/all", response_model=List[ItemShort])
def read_items(offset: int=0, limit: int=Query(default=100, le=100), session:Session = Depends(db_core.get_session)):
    items = db.read_items(session, offset, limit)
    return items

@router.get("/{item_id}", response_model=ItemShort)
def read_item(item_id: int, session:Session = Depends(db_core.get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


#-- UPDATE
@router.patch("/{item_id}", response_model=ItemShort)
def update_item(item_id: int, item: ItemUpdate, session:Session = Depends(db_core.get_session)):
    try:
        updated_item = db.update_item(session, item_id, item)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Item not updated")
    return updated_item


#-- DELETE
@router.delete("/{item_id}")
def delete_item(item_id: int, session:Session = Depends(db_core.get_session)):
    try:
        db.delete_item(session, item_id)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Item not updated")
    return {'ok': f'deleted Item {item_id}'}
