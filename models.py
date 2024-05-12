#models/item.py
#Good template: can be replicated for other item types
from typing import List, Optional

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship, AutoString

#--- GROUP (generic group of Items) Class Options
#Ref: Teams: https://sqlmodel.tiangolo.com/tutorial/fastapi/teams/
class GroupBase(SQLModel, table=False):
    name: str = Field(index=True)
    param2: str

class Group(GroupBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    items: List['Item'] = Relationship(back_populates='group')

class GroupCreate(GroupBase):
    pass

class GroupRead(GroupBase):
    id: str

class GroupShort(GroupBase):
    group_id: str
    name: str

class GroupUpdate(GroupBase):
    group_id: str
    item_id: str
    name: Optional[str] = None
    param2: Optional[str] = None

    
#--- ITEM (generic) Class Options 
class ItemBase(SQLModel, table=False):
    name: str = Field(index=True)
    email: EmailStr = Field(unique=True, index=True, sa_type=AutoString)
    phone: str = Field()
    group_id: Optional[int] = Field(default=None, foreign_key='group.id')
#Autostring ref: https://github.com/tiangolo/sqlmodel/discussions/730

class Item(ItemBase, table=True, extend_existing=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    group: Optional[Group] = Relationship(back_populates='items')
    param1: Optional[str] = ''

class ItemCreate(ItemBase):
    pass

class ItemRead(ItemBase):
    id: str

class ItemShort(ItemBase):
    id: str
    name: str
    
class ItemUpdate(ItemBase):
    item_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    group_id: Optional[int] = None

