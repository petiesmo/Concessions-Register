#app.py
from sqlmodel import SQLModel, create_engine, Session

from models import Project, Customer

#-- CRUD app
sqlite_file_name = r'C:\Users\pjsmole\Documents\Github\crudform\database4.db'
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def create_customers(cdata: list[dict]):
    with Session(engine) as session:
        for c in cdata:    
            customer = Customer(**c)
            session.add(customer)
        session.commit()

def create_projects(pdata: list[dict]):
    with Session(engine) as session:
        for p in pdata:    
            project = Project(**p)
            session.add(project)
        session.commit()

def main():
    create_db_and_tables()
    clist = [
        {"name": "Joe"}
    ]
    plist = [
        {"height": "75"}
    ]
    create_customers(clist)
    create_projects(plist)

if __name__ == '__main__':
    main()