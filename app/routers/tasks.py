from typing import Annotated

from fastapi import APIRouter, Depends, Query

from .. import schemas
from ..dependencies import get_task_service
from ..services import TaskService

router = APIRouter(prefix="/api", tags=["tasks"])
Service = Annotated[TaskService, Depends(get_task_service)]


@router.get("/projects/{project_id}/tasks", response_model=list[schemas.TaskOut])
def list_tasks(
    project_id: int,
    service: Service,
    done: bool | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return service.list(project_id, done, limit, offset)


@router.post("/projects/{project_id}/tasks", response_model=schemas.TaskOut, status_code=201)
def create_task(project_id: int, data: schemas.TaskIn, service: Service):
    return service.create(project_id, data)


@router.patch("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, data: schemas.TaskUpdate, service: Service):
    return service.update(task_id, data)


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, service: Service):
    service.delete(task_id)
