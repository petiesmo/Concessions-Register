#models.py
#Good template: can be replicated for other item types
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any
from uuid import uuid4

from pydantic import EmailStr, BaseModel, ConfigDict
from sqlalchemy import ForeignKey, DateTime, func
from sqlmodel import SQLModel, Field, Column, Relationship, AutoString, JSON

#Autostring ref for EmailStr and HttpUrl types: https://github.com/tiangolo/sqlmodel/discussions/730
#Ref: Teams: https://sqlmodel.tiangolo.com/tutorial/fastapi/teams/
    #Autostring ref: https://github.com/tiangolo/sqlmodel/discussions/730
    #remember: response_model_exclude_unset parameter

#--- CORE MODELS
class SimpleIDModel(BaseModel):
    id: int


class UUIDIDModel(BaseModel):
    id: str = Field(default_factory=uuid4)


class TimestampModel(BaseModel):
    created_at: datetime = Field(default_factory=datetime.now)
    #updated_at: Optional[datetime] = Field(sa_column=Column(DateTime(), onupdate=func.now()), default=None)
    #Datetime stuff:  https://github.com/tiangolo/sqlmodel/issues/594


class EventTimestamp(BaseModel):
    occured_at: datetime | None


def SKU_number():
    #Creates unique SKU
    #TODO: implement this
    pass

#--- BASE Class for SQLModel objects
class BaseSQLModel(SQLModel, TimestampModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    

#--- USER class (for users of the API)
#class User(BaseSQLModel, table=True, extend_existing=True):
#    email: str
#    hashed_password: str


#--- CUSTOMER class options ---
class CustomerBase(SQLModel):
    name: str = Field(index=True, nullable=False)
    badge_id: str | None = Field(unique_items=True, index=True, default=None)
    acct_balance: float = Field(default=0.00, nullable=False)
    staff: bool = Field(index=True, nullable=False, default=False)
    active: bool = Field(index=True, nullable=False, default=True)
    allow_neg_balance: bool = Field(nullable=False, default=False)

    model_config = ConfigDict(arbitrary_types_allowed=True, str_strip_whitespace=True)


class CustomerCreate(CustomerBase):
    pass


class Customer(BaseSQLModel, CustomerCreate, table=True, extend_existing=True):
    transactions: list['Transaction'] = Relationship(back_populates='customer')
    
    @property
    def tx_count(self):
        return len(self.transactions)


class CustomerRead(CustomerBase):
    id: int
    transactions: list['Transaction']


class CustomerShort(CustomerBase):
    id: int


#Update Ref: https://sqlmodel.tiangolo.com/tutorial/fastapi/update/
class CustomerUpdate(SQLModel):
    updated_at: datetime = Field(default_factory=datetime.now)
    name: str | None = None
    badge_id: str | None = None
    staff: bool | None = None
    acct_balance: float | None = None



#--- IMPORTANT Linkage for a Many-to-Many relationship (in this case, between Transactions & Items)
#Ref: https://sqlmodel.tiangolo.com/tutorial/many-to-many/create-models-with-link/
#class TxItemLink(SQLModel, table=True):
    #tx_id: int | None = Field(default=None, foreign_key="transaction.id", primary_key=True)
    #item_id: int | None = Field(default=None, foreign_key="item.id", primary_key=True)


#--- Product Class Options ---
class ProductBase(SQLModel):
    name: str = Field(nullable=False)
    price: float = Field(default=0.00, nullable=False)

    model_config = ConfigDict(arbitrary_types_allowed=True, str_strip_whitespace=True)


class ProductCreate(ProductBase):
    SKU: str = Field(unique_items=True, nullable=False, index=True)   #default_factory=SKU_number
    qty: float = Field(default=0)
    description: str = Field(default='')
    emoji: str = Field(default='')


class Product(BaseSQLModel, ProductCreate, table=True, extend_existing=True):
    pass


class ProductRead(ProductCreate):
    id:int


class ProductShort(ProductBase):
    id:int
    SKU: str
    emoji: str


class ProductUpdate(SQLModel):
    updated_at: datetime = Field(default_factory=datetime.now)    
    name: str | None = None
    price: float | None = None
    SKU: str | None = None
    description: str | None = None
    qty: float | None = None
    emoji: str | None = None


#--- Transaction SubClasses ---
class Payment(BaseModel):
    coupon: float = 0.00
    cash: float = 0.00
    account: float = 0.00

class LineItem(BaseModel):
    item_id: int
    name: str
    price: float
    qty: int|float = 0
    
    @property
    def subtotal(self) -> float:
        return round(self.price * self.qty, 2)


#--- TX = Transaction (generic) Class Options 
class TxType(Enum):
    PURCHASE = 1
    CASH_INOUT = 2
    ADJ_BAL = 3

class TxBase(SQLModel):
    customer_id: int | None = Field(default=None, foreign_key='customer.id')
    total: float = Field(default=0.00)
    txtype: TxType = Field(default=TxType.PURCHASE)

    model_config = ConfigDict(arbitrary_types_allowed=True, str_strip_whitespace=True)


class TxCreate(TxBase):
    cart: List[LineItem] = Field(default_factory=list, sa_column=Column(JSON))
    pmt: Payment = Field(default_factory=dict, sa_column=Column(JSON))
    note: str|None = Field(default=None)
    
    class Config:
        from_attributes = True  # Allows using ORM objects with Pydantic models


class Transaction(BaseSQLModel, TxCreate, table=True, extend_existing=True):
    customer: Customer | None = Relationship(back_populates='transactions')


class TxRead(TxCreate):
    id: int


class TxShort(TxBase):
    id: int


class TxUpdate(SQLModel):
    updated_at: datetime = Field(default_factory=datetime.now)
    customer_id: Optional[int]
    items: Optional[List]
    total: Optional[float]