from fastapi import APIRouter

from .. import schemas
from ..dependencies import PageDep
from ..dependencies import ProjectServiceDep as Service

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[schemas.ProjectOut])
def list_projects(service: Service, page: PageDep):
    return service.list(page)


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
