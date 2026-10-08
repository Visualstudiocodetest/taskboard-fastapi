"""Wiring: builds the object graph per request (dependency injection)."""
from fastapi import Depends
from sqlalchemy.orm import Session

from .database import get_db
from .repositories import ProjectRepository, TaskRepository
from .services import ProjectService, TaskService


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(ProjectRepository(db))


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(TaskRepository(db), ProjectRepository(db))
