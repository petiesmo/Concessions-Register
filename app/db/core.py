#app/db/core.py
#Core database functions

from sqlmodel import SQLModel, Session, create_engine

#--- Database
sqlite_file_name = "database.db"
DATABASE_URL = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

def create_db_and_tables(engine):
    SQLModel.metadata.create_all(bind=engine)

def get_session():
    session = Session(engine)
    yield session
    session.close()

class NotFoundError(Exception):
    pass