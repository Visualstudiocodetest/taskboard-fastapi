"""Wiring: builds the object graph per request (dependency injection)."""
from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from .database import get_db
from .repositories import ProjectRepository, TaskRepository
from .schemas import Page
from .services import ProjectService, TaskService


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(ProjectRepository(db))


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(TaskRepository(db), ProjectRepository(db))


def get_page(limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)) -> Page:
    return Page(limit, offset)


# Reusable annotated types so routers just declare `service: ProjectServiceDep`.
ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]
TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
PageDep = Annotated[Page, Depends(get_page)]
