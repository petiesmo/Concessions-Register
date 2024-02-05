#models.py
from datetime import datetime
from enum import Enum
from uuid import uuid1
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

#--- CUSTOMER Class Options
class CustomerBase(SQLModel, table=False):
    name: str = Field(index=True)
    email: EmailStr = Field(index=True)
    phone: str = Field()
    #projects: list[str] = []

class Customer(CustomerBase, table=True, extend_existing=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class CustomerCreate(CustomerBase):
    pass

class CustomerRead(CustomerBase):
    id: str

class CustomerShort(CustomerBase):
    id: str
    name: str
    
class CustomerUpdate(CustomerBase):
    customer_id: str
    date_submit: datetime
    date_needed: datetime


class SType(Enum):
    E2E = 'Edge to Edge'
    BC = 'Border Corner'
    CBW = 'Custom Block Work'

#--- PROJECT Class Options
class ProjectBase(SQLModel, table=False):
    date_submit: datetime = Field(default_factory=datetime.today())
    date_needed: datetime = Field(default_factory=datetime.today())
    customer: Optional[int] = Field(default=None, foreign_key="customer.id")
    height:int = Field(default=50, gt=0)
    width:int = Field(default=50, gt=0)
    hborder:int = Field(default=0, ge=0)
    wborder:int = Field(default=0, ge=0)
    stype:SType = Field(default=SType.E2E)
    border_corner:bool = Field(default=False)
    binding:bool = Field(default=False)

    @property
    def estimated_cost(self):
        return 1

class Project(ProjectBase, table=True, extend_existing=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class ProjectCreate(ProjectBase):
    pass

class ProjectRead(ProjectBase):
    id: str

class ProjectShort(ProjectBase):
    id: str
    customer_id: str
    date_submit: datetime
    date_needed: datetime
    
class ProjectUpdate(ProjectBase):
    customer_id: str
    date_submit: datetime
    date_needed: datetime