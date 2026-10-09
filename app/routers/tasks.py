from fastapi import APIRouter

from .. import schemas
from ..dependencies import PageDep
from ..dependencies import TaskServiceDep as Service

router = APIRouter(prefix="/api", tags=["tasks"])

# Tasks are created/listed under their project, but updated/deleted by their own id.


@router.get("/projects/{project_id}/tasks", response_model=list[schemas.TaskOut])
def list_tasks(project_id: int, service: Service, page: PageDep, done: bool | None = None):
    return service.list(project_id, done, page)


@router.post("/projects/{project_id}/tasks", response_model=schemas.TaskOut, status_code=201)
def create_task(project_id: int, data: schemas.TaskIn, service: Service):
    return service.create(project_id, data)


@router.patch("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, data: schemas.TaskUpdate, service: Service):
    return service.update(task_id, data)


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, service: Service):
    service.delete(task_id)
