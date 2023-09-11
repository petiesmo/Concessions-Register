#api.py
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select

from models import Project

#--- Database
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


#-- CRUD app

app = FastAPI()


app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/projects/")
def create_project(project: Project):
    with Session(engine) as session:
        session.add(project)
        session.commit()
        session.refresh(project)
        return project


@app.get("/projects/")
def read_projects():
    with Session(engine) as session:
        heroes = session.exec(select(Project)).all()
        return heroes

@app.get("/projects/{project_id}")
def read_projects():
    with Session(engine) as session:
        heroes = session.exec(select(Project)).one(_id = project_id)
    return heroes

@app.patch("/projects/{project_id}", response_model=ProjectRead)
def update_project(project_id: int, hero: ProjectUpdate):
    with Session(engine) as session:
        db_project = session.get(Project, project_id)
        if not db_project:
            raise HTTPException(status_code=404, detail="Project not found")
        project_data = hero.dict(exclude_unset=True)
        for key, value in project_data.items():
            setattr(db_project, key, value)
        session.add(db_project)
        session.commit()
        session.refresh(db_project)
        return db_project