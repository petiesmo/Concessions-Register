#db_ops.py
'''
Generic CRUD Database functions.  
CRUDBase class accepts a model type (rather than re-writing same functions for each model)
'''

from typing import List, Type

from sqlmodel import Session, select as sqlselect

from .models import BaseSQLModel
from .core import NotFoundError

# Base class for CRUD operations
class CRUDBase():

    def __init__(self, model_type: Type[BaseSQLModel]):
        self.model_type = model_type


    def create_one(self, session: Session, data) -> BaseSQLModel:
        db_model = self.model_type(**data)
        session.add(db_model)
        session.commit()
        session.refresh(db_model)
        return db_model


    def create_many(self, session: Session, data_list: List) -> List[BaseSQLModel]:
        new_models = []
        for data in data_list:
            db_model = self.model_type.model_validate(data)
            session.add(db_model)
            new_models.append(db_model)
        session.commit()
        for new_model in new_models:
            session.refresh(new_model)
        return new_models


    def read_all(self, session: Session, offset: int = 0, limit: int = 100):
        return session.exec(sqlselect(self.model_type).offset(offset).limit(limit)).all()


    def read_one(self, session: Session, item_id: int) -> BaseSQLModel:
        model = session.get(self.model_type, item_id)
        if not model:
            raise NotFoundError(f"{self.model_type.__name__} {item_id} not found")
        return model


    def update_one(self, session: Session, item_id: int, data:BaseSQLModel) -> BaseSQLModel:
        model_in_db = session.get(self.model_type, item_id)
        if not model_in_db:
            raise NotFoundError(f"{self.model_type.__name__} {item_id} not found")
        data_dict = data.model_dump(exclude_unset=True)
        for key, value in data_dict.items():
            setattr(model_in_db, key, value)
        session.add(model_in_db)
        session.commit()
        session.refresh(model_in_db)
        return model_in_db


    def delete_one(self, session: Session, item_id: int) -> bool:
        model_in_db = session.get(self.model_type, item_id)
        if not model_in_db:
            raise NotFoundError(f"{self.model_type.__name__} {item_id} not found")
        session.delete(model_in_db)
        session.commit()
        return True

    '''#______HOLD______  Still evaluating these
    def create_transaction_with_update(session: Session, transaction_data: dict):
        # Create the transaction
        transaction = Transaction(**transaction_data)
        session.add(transaction)
        session.commit()

        # Update the corresponding customer with the new transaction ID
        customer = session.get(Customer, transaction.customer_id)
        customer.transaction_ids.append(transaction.id)
        session.commit()

    def delete_transaction_with_update(session: Session, transaction_id: int):
        # Get the transaction to be deleted
        transaction = session.get(Transaction, transaction_id)
        if transaction:
            # Remove the transaction ID from the corresponding customer
            customer = session.get(Customer, transaction.customer_id)
            if transaction.id in customer.transaction_ids:
                customer.transaction_ids.remove(transaction.id)
            session.delete(transaction)
            session.commit()
    '''