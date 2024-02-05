#router/items.py
#Defines API functions at the endpoints
#Good template: Can be replicated and adjusted for other item types.
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from sqlmodel import select as sqlselect

from app.models.item import Item, ItemShort, ItemCreate, ItemUpdate

#Note: The 'get_session' dependency is brought in at the app level (api.py -> app)
router = APIRouter(
    prefix='/items',
    tags=['items'],
    dependencies=[],
    responses={404: {'description': 'Not found'}}
)

#-- CREATE
@router.post("/", response_model=ItemShort)
def create_item(item: ItemCreate):
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

#-- READ
@router.get("/", response_model=ItemShort)
def read_items(offset: int=0, limit: int=Query(default=100, le=100)):
    items = Session.exec(sqlselect(Item).offset(offset).limit(limit)).all()
    return items

@router.get("/{item_id}", response_model=ItemShort)
def read_item(item_id: int):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

#-- UPDATE
@router.patch("/{item_id}", response_model=ItemShort)
def update_item(item_id: int, item: ItemUpdate):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item_data = item.dict(exclude_unset=True)
    for key, value in item_data.items():
        setattr(item, key, value)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

#-- DELETE
@router.delete("/{item_id}")
def delete_item(item_id: int):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(item)
    session.commit()
    return {'ok': f'deleted Item {item_id}'}