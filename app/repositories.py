"""Data access layer: the only place that knows about SQL."""
from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models
from .exceptions import ConflictError
from .schemas import Page

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Generic get/save/delete; subclasses only set `model` and add their own queries."""

    model: type[T]
    conflict_message = "Conflicts with an existing record"

    def __init__(self, db: Session):
        self.db = db

    def get(self, entity_id: int) -> T | None:
        return self.db.get(self.model, entity_id)

    def save(self, entity: T) -> T:
        self.db.add(entity)
        try:
            self.db.commit()
        except IntegrityError as err:  # e.g. unique constraint violated
            self.db.rollback()
            raise ConflictError(self.conflict_message) from err
        return entity

    def delete(self, entity: T) -> None:
        self.db.delete(entity)
        self.db.commit()


class ProjectRepository(BaseRepository[models.Project]):
    model = models.Project
    conflict_message = "A project with this name already exists"

    def count_tasks(self, project_id: int) -> int:
        stmt = select(func.count()).where(models.Task.project_id == project_id)
        return self.db.scalar(stmt) or 0

    def list_with_counts(self, page: Page) -> list[tuple[models.Project, int]]:
        # One JOIN + GROUP BY instead of one COUNT query per project (avoids N+1).
        stmt = (
            select(models.Project, func.count(models.Task.id))
            .outerjoin(models.Task)
            .group_by(models.Project.id)
            .order_by(models.Project.id)
            .limit(page.limit)
            .offset(page.offset)
        )
        return [(p, c) for p, c in self.db.execute(stmt)]


class TaskRepository(BaseRepository[models.Task]):
    model = models.Task

    def list_for_project(
        self, project_id: int, done: bool | None, page: Page
    ) -> list[models.Task]:
        stmt = select(models.Task).where(models.Task.project_id == project_id)
        if done is not None:
            stmt = stmt.where(models.Task.done == done)
        stmt = stmt.order_by(models.Task.priority, models.Task.id)
        return list(self.db.scalars(stmt.limit(page.limit).offset(page.offset)))
