#app/db/transactions.py
#Database functions for the Transactions table
from typing import List

from sqlmodel import Session
from sqlmodel import select as sqlselect

from models import Transaction, TxShort, TxCreate, TxUpdate
from .core import NotFoundError


def create_one_transaction(session:Session, transaction: TxCreate) -> Transaction:
    db_transaction = Transaction.model_validate(transaction)
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction


def create_many_transactions(session:Session, transactions: List[TxCreate]) -> List[Transaction]:
    new_transactions = list()
    for transaction in transactions:
        db_transaction = Transaction.model_validate(transaction)
        new_transactions.append(db_transaction)
        session.add(db_transaction)
    session.commit()

    for nc in new_transactions:
        session.refresh(nc)
    return new_transactions


def read_all_transactions(session:Session, offset: int=0, limit: int=100):
    transactions = session.exec(sqlselect(Transaction).offset(offset).limit(limit)).all()
    return transactions


def read_transaction(transaction_id: int, session:Session):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise NotFoundError(f"Transaction {transaction_id} not found")
    return transaction


def update_transaction(session:Session, transaction_id: int, transaction: TxUpdate):
    transaction_in_db = session.get(Transaction, transaction_id)
    if not transaction_in_db:
        raise NotFoundError(f"Transaction {transaction_id} not found")
    transaction_data = transaction.model_dump(exclude_unset=True)
    for key, value in transaction_data.items():
        setattr(transaction, key, value)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


def delete_transaction(session:Session, transaction_id: int):
    transaction_in_db = session.get(Transaction, transaction_id)
    if not transaction_in_db:
        raise NotFoundError(f"Transaction {transaction_id} not found")
        return False
    session.delete(transaction_in_db)
    session.commit()
    return True