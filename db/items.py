#app/db/items.py
#Database functions for the items table
#Good template for other types of items/groups
from typing import List

from sqlmodel import Session
from sqlmodel import select as sqlselect

from models import Item, ItemShort, ItemCreate, ItemUpdate
from .core import NotFoundError


def create_one_item(session:Session, item: ItemCreate) -> Item:
    db_item = Item.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def create_many_items(session:Session, items: List[ItemCreate]) -> List[Item]:
    new_items = list()
    for item in items:
        db_item = Item.model_validate(item)
        new_items.append(db_item)
        session.add(db_item)
    session.commit()

    for nc in new_items:
        session.refresh(nc)
    return new_items


def read_all_items(session:Session, offset: int=0, limit: int=100):
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