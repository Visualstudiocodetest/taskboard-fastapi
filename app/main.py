from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_db

Base.metadata.create_all(engine)

app = FastAPI(title="TaskBoard")
STATIC = Path(__file__).resolve().parent.parent / "static"


def get_project_or_404(db: Session, project_id: int) -> models.Project:
    project = db.get(models.Project, project_id)
    if project is None:
        raise HTTPException(404, f"Project {project_id} not found")
    return project


def project_out(db: Session, p: models.Project) -> schemas.ProjectOut:
    count = db.scalar(select(func.count()).where(models.Task.project_id == p.id))
    return schemas.ProjectOut(id=p.id, name=p.name, description=p.description, task_count=count or 0)


# ---- Projects (full CRUD) ----
@app.get("/api/projects", response_model=list[schemas.ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return [project_out(db, p) for p in db.scalars(select(models.Project).order_by(models.Project.id))]


@app.post("/api/projects", response_model=schemas.ProjectOut, status_code=201)
def create_project(data: schemas.ProjectIn, db: Session = Depends(get_db)):
    p = models.Project(**data.model_dump())
    db.add(p)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "A project with this name already exists")
    return project_out(db, p)


@app.get("/api/projects/{project_id}", response_model=schemas.ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    return project_out(db, get_project_or_404(db, project_id))


@app.put("/api/projects/{project_id}", response_model=schemas.ProjectOut)
def update_project(project_id: int, data: schemas.ProjectIn, db: Session = Depends(get_db)):
    p = get_project_or_404(db, project_id)
    for k, v in data.model_dump().items():
        setattr(p, k, v)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "A project with this name already exists")
    return project_out(db, p)


@app.delete("/api/projects/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db.delete(get_project_or_404(db, project_id))
    db.commit()


# ---- Tasks (belong to a project) ----
@app.get("/api/projects/{project_id}/tasks", response_model=list[schemas.TaskOut])
def list_tasks(project_id: int, done: bool | None = None, db: Session = Depends(get_db)):
    get_project_or_404(db, project_id)
    q = select(models.Task).where(models.Task.project_id == project_id)
    if done is not None:
        q = q.where(models.Task.done == done)
    return db.scalars(q.order_by(models.Task.priority, models.Task.id)).all()


@app.post("/api/projects/{project_id}/tasks", response_model=schemas.TaskOut, status_code=201)
def create_task(project_id: int, data: schemas.TaskIn, db: Session = Depends(get_db)):
    get_project_or_404(db, project_id)
    t = models.Task(project_id=project_id, **data.model_dump())
    db.add(t)
    db.commit()
    return t


def get_task_or_404(db: Session, task_id: int) -> models.Task:
    t = db.get(models.Task, task_id)
    if t is None:
        raise HTTPException(404, f"Task {task_id} not found")
    return t


@app.patch("/api/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, data: schemas.TaskUpdate, db: Session = Depends(get_db)):
    t = get_task_or_404(db, task_id)
    for k, v in data.model_dump(exclude_unset=True).items():
        if v is None:
            raise HTTPException(422, f"{k} cannot be null")
        setattr(t, k, v)
    db.commit()
    return t


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db.delete(get_task_or_404(db, task_id))
    db.commit()


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
