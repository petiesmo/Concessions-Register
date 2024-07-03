#routers/tx.py
#Defines API functions at the endpoints
#Good template: Can be replicated and adjusted for other item types.
#Many ideas from: https://github.com/ArjanCodes/examples/blob/main/2023/fastapi-router/
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session

from db.models import Transaction, TxCreate, TxUpdate, TxShort, TxType 
from db.models import Customer, CustomerUpdate
from db.core import get_session
from db.db_ops import CRUDBase

items = CRUDBase(Transaction)
customers = CRUDBase(Customer)

router = APIRouter(
    prefix='/tx',
    tags=['transactions'],
    dependencies=[],
    responses={
        400: {'description': 'Bad request. Record not created/updated'},
        404: {'description': 'Non-specific error (Record Not found)'}}
)

@router.get("")
def return_html_form():
    basic_screen = HTMLResponse("<html><body><h1>The Most Basic TX ever</h1></body></html>")
    return basic_screen


#-- CREATE
@router.post("/{txtype}")
def create_item(txtype:TxType, data: TxCreate, session: Session = Depends(get_session)):
    '''Create a new transaction AND update customer balance accordingly'''
    try:
        # Create the transaction
        tx_dict = data.model_dump()
        print(f'Received new tx: {tx_dict}')
        tx_dict['txtype'] = txtype
        item = items.create_one(session, tx_dict)

        # Fetch the associated customer
        customer = customers.read_one(session, item.customer_id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        
        # Update the customer's balance
        if txtype == TxType.PURCHASE:
            new_balance = round(customer.acct_balance - data.pmt.account, 2)  # Adjust the balance by the payment applied to the account
        else:
            new_balance = round(customer.acct_balance + data.pmt.cash + data.pmt.account, 2)  # Adjust the balance by the cash or acct adjustments
        
        customer_update = CustomerUpdate(acct_balance=new_balance)
        customers.update_one(session, customer.id, customer_update)
        
        # Return the created transaction
        session.refresh(item)
        #return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(item))
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={'message': f'Tx {item.id} created successfully', 'new_tx_id': item.id})

    except ValueError as e:
        print(f'Validation error: {e}')
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


#-- READ
@router.get("/all", response_model=List[TxShort])
def read_items(offset: int = 0, limit: int = Query(default=100, le=100), session: Session = Depends(get_session)):
    records = items.read_all(session, offset, limit)
    return records


@router.get("/{item_id}", response_model=Transaction)
def read_item(item_id: int, session: Session = Depends(get_session)):
    try:
        record = items.read_one(session, item_id)
        if not record:
            raise ValueError(f'{item_id} not found')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e
    return record


#-- UPDATE
@router.patch("/{item_id}", response_model=TxShort)
def update_item(item_id: int, data: TxUpdate, session: Session = Depends(get_session)):
    try:
        updated_item = items.update_one(session, item_id, data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from e
    return updated_item


#-- DELETE
@router.delete("/{item_id}")
def delete_item(item_id: int, session: Session = Depends(get_session)):
    try:
        items.delete_one(session, item_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from e
    return {'ok': f'deleted Tx {item_id}'}
