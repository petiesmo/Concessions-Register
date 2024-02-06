#app/db/items.py
#Database functions for the items table

from sqlmodel import Session
from sqlmodel import select as sqlselect

from app.models.item import Item, ItemShort, ItemCreate, ItemUpdate
from .core import NotFoundError


def create_item(session:Session, item: ItemCreate):
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def read_items(session:Session, offset: int=0, limit: int=100):
    items = session.exec(sqlselect(Item).offset(offset).limit(limit)).all()
    return items


def read_item(item_id: int, session:Session):
    item = session.get(Item, item_id)
    if not item:
        raise NotFoundError(f"Item {item_id} not found")
    return item


def update_item(session:Session, item_id: int, item: ItemUpdate):
    item_in_db = session.get(Item, item_id)
    if not item_in_db:
        raise NotFoundError(f"Item {item_id} not found")
    item_data = item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(item, key, value)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def delete_item(session:Session, item_id: int):
    item_in_db = session.get(Item, item_id)
    if not item_in_db:
        raise NotFoundError(f"Item {item_id} not found")
        return False
    session.delete(item_in_db)
    session.commit()
    return True