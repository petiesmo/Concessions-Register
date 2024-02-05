#api.py
from fastapi import FastAPI
from fastapi.exceptions import HTTPException

import sqlmodel
from sqlmodel import Field, Session, SQLModel, create_engine
from sqlmodel import select as sqlselect

from models import Project, ProjectShort, ProjectCreate, ProjectUpdate

#--- Database
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


#-- CRUD app
app = FastAPI()
#TODO: Convert to using Routers

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

#-- CREATE
@app.post("/projects/")
def create_project(project: Project):
    with Session(engine) as session:
        session.add(project)
        session.commit()
        session.refresh(project)
        return project

#-- READ
@app.get("/projects/", response_model=ProjectShort)
def read_projects():
    with Session(engine) as session:
        projects = session.exec(sqlselect(Project)).all()
        return projects

@app.get("/projects/{project_id}", response_model=ProjectShort)
def read_project(project_id: int):
    with Session(engine) as session:
        project = session.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
    return project

#-- UPDATE
@app.patch("/projects/{project_id}", response_model=ProjectShort)
def update_project(project_id: int, project: ProjectUpdate):
    with Session(engine) as session:
        project = session.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        project_data = project.dict(exclude_unset=True)
        for key, value in project_data.items():
            setattr(project, key, value)
        session.add(project)
        session.commit()
        session.refresh(project)
        return project

#-- DELETE
@app.delete("/projects/{project_id}")
def delete_project(project_id: int):
    with Session(engine) as session:
        project = session.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        session.delete(project)
        session.commit()
        return {'ok': f'deleted Project {project_id}'}