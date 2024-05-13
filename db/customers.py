#app/db/customers.py
#Database functions for the customers table
#Good template for other types of customers/groups
from typing import List

from sqlmodel import Session
from sqlmodel import select as sqlselect

from models import Customer, CustomerShort, CustomerCreate, CustomerUpdate
from .core import NotFoundError


def create_one_customer(session:Session, customer: CustomerCreate) -> Customer:
    db_customer = Customer.model_validate(customer)
    session.add(db_customer)
    session.commit()
    session.refresh(db_customer)
    return db_customer


def create_many_customers(session:Session, customers: List[CustomerCreate]) -> List[Customer]:
    new_customers = list()
    for customer in customers:
        db_customer = Customer.model_validate(customer)
        new_customers.append(db_customer)
        session.add(db_customer)
    session.commit()

    for nc in new_customers:
        session.refresh(nc)
    return new_customers


def read_all_customers(session:Session, offset: int=0, limit: int=100):
    customers = session.exec(sqlselect(Customer).offset(offset).limit(limit)).all()
    return customers


def read_customer(customer_id: int, session:Session):
    customer = session.get(Customer, customer_id)
    if not customer:
        raise NotFoundError(f"Customer {customer_id} not found")
    return customer


def update_customer(session:Session, customer_id: int, customer: CustomerUpdate):
    customer_in_db = session.get(Customer, customer_id)
    if not customer_in_db:
        raise NotFoundError(f"Customer {customer_id} not found")
    customer_data = customer.model_dump(exclude_unset=True)
    for key, value in customer_data.items():
        setattr(customer, key, value)
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


def delete_customer(session:Session, customer_id: int):
    customer_in_db = session.get(Customer, customer_id)
    if not customer_in_db:
        raise NotFoundError(f"Customer {customer_id} not found")
        return False
    session.delete(customer_in_db)
    session.commit()
    return True