from typing import Annotated

from fastapi import APIRouter, Depends, Query

from .. import schemas
from ..dependencies import get_project_service
from ..services import ProjectService

router = APIRouter(prefix="/api/projects", tags=["projects"])
Service = Annotated[ProjectService, Depends(get_project_service)]


@router.get("", response_model=list[schemas.ProjectOut])
def list_projects(
    service: Service,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return service.list(limit, offset)


@router.post("", response_model=schemas.ProjectOut, status_code=201)
def create_project(data: schemas.ProjectIn, service: Service):
    return service.create(data)


@router.get("/{project_id}", response_model=schemas.ProjectOut)
def get_project(project_id: int, service: Service):
    return service.get(project_id)


@router.put("/{project_id}", response_model=schemas.ProjectOut)
def update_project(project_id: int, data: schemas.ProjectIn, service: Service):
    return service.update(project_id, data)


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, service: Service):
    service.delete(project_id)
