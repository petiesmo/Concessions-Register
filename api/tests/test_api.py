#test_api.py
#Pattern from: https://github.com/ArjanCodes/examples/blob/main/2023/apitesting/test_api.py

from fastapi.testclient import TestClient
from httpx import Client
from sqlmodel import Session, create_engine, StaticPool

import app.api as api
import app.db.core as db

# Setup the TestClient
client = TestClient(api.app)
http_client = Client(app=api.app)

# Setup the in-memory SQLite database for testing
DATABASE_URL = "sqlite:///:memory:"
connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args, poolclass=StaticPool)

TestingSessionLocal = Session(autocommit=False, autoflush=False, bind=engine)


# Dependency to override the get_db dependency in the main app
def override_get_db():
    database = TestingSessionLocal
    yield database
    database.close()

api.app.dependency_overrides[db.get_session] = override_get_db
