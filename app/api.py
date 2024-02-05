#api.py
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine
from sqlmodel import select as sqlselect

#from models.models import Project, ProjectShort, ProjectCreate, ProjectUpdate
from app.routers import items  #, customers, projects

#--- Database
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    #Stuff to do on startup
    create_db_and_tables()
    yield
    #Stuff to do on shutdown
    pass

#-- CRUD app
app = FastAPI(lifespan=lifespan, dependencies=[Depends(get_session)])
#TODO: App needs to serve the Entry Form webpage
#TODO: App needs to read the returned Form data, and make database calls accordingly


app.include_router(items.router)
#app.include_router(customers.router)
#app.include_router(projects.router)


def main():
    pass

if __name__ == '__main__':
    main()