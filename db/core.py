#db/core.py
'''Core database functions'''
from contextlib import contextmanager, asynccontextmanager
import os

from dotenv import load_dotenv
from dotenv import dotenv_values
from sqlmodel import SQLModel, Session, create_engine
#from sqlmodel.ext.asyncio import AsyncSession, create_async_engine

#load_dotenv('../.env', override=True)
env = dotenv_values('../.env')
#--- Database
DATABASE_URL = "mysql+pymysql://user2:password2@db/mydatabase"
DATABASE_URL = env.get('DATABASE_URL', "sqlite:///./test_local.db")
print(f'Using db: {DATABASE_URL}')
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith('sqlite') else {}

# Synchronous Engine and Session
sync_engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)
SyncSessionLocal = Session(autocommit=False, autoflush=False, bind=sync_engine)

# Asynchronous Engine and Session
#async_engine = create_async_engine(DATABASE_URL, echo=True)
#AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)

def create_db_and_tables():
    SQLModel.metadata.create_all(bind=sync_engine)


def get_session() -> Session:
    session = SyncSessionLocal
    try:
        yield session
    finally:
        session.close()


class NotFoundError(Exception):
    pass