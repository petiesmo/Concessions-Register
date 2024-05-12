from fastapi import APIRouter

router = APIRouter()

#-- CREATE
@router.post("/projects/")
def create_project(project: Project):
    with Session(engine) as session:
        session.add(project)
        session.commit()
        session.refresh(project)
        return project

#-- READ
@router.get("/projects/", response_model=ProjectShort)
def read_projects():
    with Session(engine) as session:
        projects = session.exec(sqlselect(Project)).all()
        return projects

@router.get("/projects/{project_id}", response_model=ProjectShort)
def read_project(project_id: int):
    with Session(engine) as session:
        project = session.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
    return project

#-- UPDATE
@router.patch("/projects/{project_id}", response_model=ProjectShort)
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
@router.delete("/projects/{project_id}")
def delete_project(project_id: int):
    with Session(engine) as session:
        project = session.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        session.delete(project)
        session.commit()
        return {'ok': f'deleted Project {project_id}'}