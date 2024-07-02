#router/items.py
#Defines API functions at the endpoints
#Good template: Can be replicated and adjusted for other item types 
#(Find/Replace Item with another Class)(any lowercase 'item' can stay the same).
#Many ideas from: https://github.com/ArjanCodes/examples/blob/main/2023/fastapi-router/
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from sqlmodel import Session

from ...db.models import Item, ItemCreate, ItemUpdate, ItemShort
from ...db.core import get_session
from ...db.db_ops import CRUDBase

items = CRUDBase(Item)
router = APIRouter(
    prefix='/Items',
    tags=['Items'],
    dependencies=[],
    responses={
        400: {'description': 'Bad request. Record not created/updated'},
        404: {'description': 'Record Not found'}}
)

@router.get("")
def return_html_form():
    basic_screen = HTMLResponse("<html><body><h1>The Most Basic Items ever</h1></body></html>")
    return basic_screen


#-- CREATE
@router.post("/", response_model=ItemShort)
def create_item(data: ItemCreate, session:Session = Depends(get_session)):
    try:
        item = items.create_one(session, data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from e
    return item


#-- READ
@router.get("/all", response_model=List[ItemShort])
def read_items(offset: int=0, limit: int=Query(default=100, le=100), session:Session = Depends(get_session)):
    records = items.read_all(session, offset, limit)
    return records


@router.get("/{item_id}", response_model=Item)
def read_item(item_id: int, session:Session = Depends(get_session)):
    try:
        record = items.read_one(session, item_id)
        if not record:
            raise ValueError(f'{item_id} not found')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e
    return record


#-- UPDATE
@router.patch("/{item_id}", response_model=ItemShort)
def update_item(item_id: int, data: ItemUpdate, session:Session = Depends(get_session)):
    try:
        updated_item = items.update_one(session, item_id, data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from e
    return updated_item


#-- DELETE
@router.delete("/{item_id}")
def delete_item(item_id: int, session:Session = Depends(get_session)):
    try:
        items.delete_one(session, item_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from e
    return {'ok': f'deleted Tx {item_id}'}
