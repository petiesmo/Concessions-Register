#TODO: Figure out this PyTest thing!
import pytest
from dotenv import load_dotenv  #reads key-value pairs from a .env file and can set them as environment variables
from dotenv import dotenv_values #The function dotenv_values works more or less the same way as load_dotenv, except it doesn't touch the environment, it just returns a dict with the values parsed from the .env file.
from sqlmodel import SQLModel, Session, create_engine, StaticPool
from sqlmodel import select as sqlselect

from ..models.models import Item, ItemShort, ItemCreate, ItemUpdate
from .core import create_db_and_tables
from .items import create_item, read_items, read_item, update_item, delete_item

#----- SETUP & FIXTURES -----
# Setup the in-memory SQLite database for testing
DATABASE_URL = "sqlite:///:memory:"
connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args, poolclass=StaticPool)

@pytest.fixture
def db_session():
    #Create tables in the test database
    create_db_and_tables(engine=engine)
    session = Session(autocommit=False, autoflush=False, bind=engine)  #TestingSessionLocal
    yield session
    session.rollback()  #Replaces teardown "drop_all"?
    session.close()    

DATA1 = {'name': 'John Doe', 'email': 'JohnDoe@dunno.com', 'phone':'999-999-9999'}
DATA2 = {'id': 999, 'name': 'Jane Doe', 'email': 'JaneDoe@dunno.com', 'phone':'999-999-9998'}
DATA2u = {'name': 'Ms. Daisy'}

@pytest.fixture
def valid_create():
    valid_create = ItemCreate(**DATA1)
    return valid_create

@pytest.fixture
def valid_item():
    valid_item = Item(**DATA2)
    return valid_item

@pytest.fixture
def updated_item():
    updated_item = ItemUpdate(**DATA2u)
    return updated_item

#----- TESTS -----
def test_create_and_read_item(db_session, valid_create):
    new_item = create_item(session=db_session, item=valid_create)
    print(new_item)
    assert type(new_item.id) == int
    db_item = read_item(session=db_session, item_id=new_item.id)
    assert db_item.name == DATA1['name']
    assert db_item.email == DATA1['email']
    assert db_item.phone == DATA1['phone']
    

def test_read_items(db_session):
    db_items = read_items(session=db_session)
    assert len(db_items) > 0

def test_read_item():
    #Tested as part of create
    assert True

def test_update_item(db_session, valid_item, updated_item):
    db_session.add(valid_item)
    db_session.commit()
    updated_item = update_item(session=db_session, item_id=valid_item.id, item=updated_item)
    db_item = read_item(session=db_session, item_id=valid_item.id)
    assert db_item.name != DATA2['name']
    assert db_item.name == DATA2u['name']
    

def test_delete_item(db_session):
    assert True


if __name__ == '__main__':
    test_update_item(db_session(), valid_item(), updated_item())