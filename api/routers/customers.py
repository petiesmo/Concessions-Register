#router/customers.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlmodel import Session

from db.models import Customer, CustomerCreate, CustomerUpdate, CustomerShort, CustomerRead
from db.core import get_session
from db.db_ops import CRUDBase

items = CRUDBase(Customer)
router = APIRouter(
    prefix='/customers',
    tags=['customers'],
    dependencies=[],
    responses={
        400: {'description': 'Bad request. Record not created/updated'},
        404: {'description': 'Record Not found'}}
)

@router.get("")
def return_html_form():
    basic_screen = HTMLResponse("<html><body><h1>The Most Basic People ever</h1></body></html>")
    return basic_screen


#-- CREATE
@router.post("/")
def create_item(data: CustomerCreate, session:Session = Depends(get_session)):
    try:
        item_dict = data.model_dump()
        print(f'Received new item: {item_dict}')
        item = items.create_one(session, item_dict)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from e
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={'message': f'Customer {item.id} created successfully', 'new_customer_id': item.id})


#-- READ
@router.get("/all", response_model=List[CustomerShort])
def read_items(offset: int=0, limit: int=Query(default=1000, le=1000), session:Session = Depends(get_session)):
    records = items.read_all(session, offset, limit)
    return records


@router.get("/{item_id}", response_model=CustomerRead)
def read_item(item_id: int, session:Session = Depends(get_session)):
    try:
        record = items.read_one(session, item_id)
        if not record:
            raise ValueError(f'{item_id} not found')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e
    return record


#-- UPDATE
@router.patch("/{item_id}", response_model=CustomerShort)
def update_item(item_id: int, data: CustomerUpdate, session:Session = Depends(get_session)):
    try:
        updated_item = items.update_one(session, item_id, data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from e
    return updated_item

@router.patch("/closeout/{item_id}", response_model=CustomerShort)
def closeout_customer(item_id: int, session:Session = Depends(get_session)):
    try:
        item = items.read_one(session, item_id)
        print(f'{item=}')
        if item.acct_balance != 0:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'message': f'Customer [{item.id}] {item.name} account balance is {item.acct_balance}.  Must be Zero to close out'})
        data = CustomerUpdate(id=item_id, active=False)
        updated_item = items.update_one(session, item_id, data)
    except Exception as e:
        raise HTTPException(e, status_code=status.HTTP_400_BAD_REQUEST) from e
    return updated_item


#-- DELETE
@router.delete("/{item_id}")
def delete_item(item_id: int, session:Session = Depends(get_session)):
    try:
        items.delete_one(session, item_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from e
    return {'ok': f'deleted Tx {item_id}'}
