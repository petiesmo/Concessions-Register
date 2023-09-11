#models.py
from datetime import datetime
from uuid import uuid1
from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select

class Project(SQLModel):
    id: str = Field(default=uuid1(), primary_key=True)
    height:int = Field(default=50)
    width:int = Field(default=50)
    hborder:int = Field(default=0)
    wborder:int = Field(default=0)
    stype:int = Field(default=0)
    border_corner:bool = Field(default=False)
    binding:bool = Field(default=False)
    date_submit: datetime = Field(default_factory=datetime.today())
    date_needed: datetime = Field(default_factory=datetime.today())
    customer_id: str = Field(default=None, foreign_key="customer.id")


class Customer(SQLModel):
    id: str = Field(default=uuid1(), primary_key=True)
    name: str = Field(index=True)
    email: str = Field(index=True)
    phone: str = Field()


