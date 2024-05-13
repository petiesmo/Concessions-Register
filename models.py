#models.py
#Good template: can be replicated for other item types
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import EmailStr, BaseModel
from sqlalchemy import ForeignKey
from sqlmodel import SQLModel, Field, Relationship, AutoString

#Autostring ref for EmailStr and HttpUrl types: https://github.com/tiangolo/sqlmodel/discussions/730
#Ref: Teams: https://sqlmodel.tiangolo.com/tutorial/fastapi/teams/
#--- CORE MODELS
class SimpleIDModel(BaseModel):
    id: int


class UUIDIDModel(BaseModel):
    id: str = Field(default_factory=uuid4)


class TimestampModel(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime]


class EventTimestamp(BaseModel):
    occured_at: Optional[datetime]


#class Service(SimpleIDModel, TimestampModel, table=True):
#    name: str = Field(nullable=False)
#    description: str = Field(nullable=False)


#--- CUSTOMER class options ---
class CustomerBase(SQLModel, table=False):
    name: str = Field(index=True, nullable=False)
    staff: bool = Field(index=True, nullable=False, default=False)
    acct_balance: float = Field(default=0.00, nullable=False)


class Customer(CustomerBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transactions: List['Transaction'] = Relationship(back_populates='customer')


class CustomerCreate(CustomerBase):
    pass


class CustomerRead(CustomerBase):
    id: int


class CustomerShort(CustomerBase):
    name: str


#Update Ref: https://sqlmodel.tiangolo.com/tutorial/fastapi/update/
class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    staff: Optional[bool] = None
    acct_balance: Optional[float] = None



#--- IMPORTANT Linkage for a Many-to-Many relationship (in this case, between Transactions & Items)
#Ref: https://sqlmodel.tiangolo.com/tutorial/many-to-many/create-models-with-link/
class TxItemLink(SQLModel, table=True):
    tx_id: int | None = Field(default=None, foreign_key="transaction.id", primary_key=True)
    item_id: int | None = Field(default=None, foreign_key="item.id", primary_key=True)



#--- TX = Transaction (generic) Class Options 
class TxBase(SQLModel, TimestampModel, table=False):
    customer_id: Optional[int] = Field(default=None, foreign_key='customer.id')
    discount: Optional[float] = Field(default=0.00)
    total: float


class Transaction(TxBase, table=True, extend_existing=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer: Customer = Relationship(back_populates='transactions')
    items: List['Item'] = Relationship(link_model=TxItemLink)
    

class TxCreate(TxBase):
    pass


class TxRead(TxBase):
    id: str


class TxShort(TxBase):
    id: str
    name: str


'''For now, Tx will only be created or deleted
class TxUpdate(SQLModel):
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    customer_id: Optional[int]
    items: Optional[List]
    total: Optional[float]
'''



#--- Items Class Options ---
class ItemBase(SQLModel, table=False):
    name: str = Field(nullable=False)
    description: Optional[str]
    price: float = Field(default=0.00, nullable=False)
    qty: float = Field(default=0.00, nullable=False)
#Autostring ref: https://github.com/tiangolo/sqlmodel/discussions/730

class Item(ItemBase, table=True, extend_existing=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ItemCreate(ItemBase):
    pass


class ItemRead(ItemBase):
    id: int
    name: str
    price: float
    qty: float


class ItemShort(ItemBase):
    id: int
    name: str
    price: float


class ItemUpdate(SQLModel):
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    qty: Optional[float]    