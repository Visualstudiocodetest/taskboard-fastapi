"""Data access layer: the only place that knows about SQL."""
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models
from .exceptions import ConflictError


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, project_id: int) -> models.Project | None:
        return self.db.get(models.Project, project_id)

    def count_tasks(self, project_id: int) -> int:
        stmt = select(func.count()).where(models.Task.project_id == project_id)
        return self.db.scalar(stmt) or 0

    def list_with_counts(self, limit: int, offset: int) -> list[tuple[models.Project, int]]:
        # One JOIN + GROUP BY instead of one COUNT query per project (avoids N+1).
        stmt = (
            select(models.Project, func.count(models.Task.id))
            .outerjoin(models.Task)
            .group_by(models.Project.id)
            .order_by(models.Project.id)
            .limit(limit)
            .offset(offset)
        )
        return [(p, c) for p, c in self.db.execute(stmt)]

    def save(self, project: models.Project) -> models.Project:
        self.db.add(project)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictError("A project with this name already exists")
        return project

    def delete(self, project: models.Project) -> None:
        self.db.delete(project)
        self.db.commit()


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, task_id: int) -> models.Task | None:
        return self.db.get(models.Task, task_id)

    def list_for_project(
        self, project_id: int, done: bool | None, limit: int, offset: int
    ) -> list[models.Task]:
        stmt = select(models.Task).where(models.Task.project_id == project_id)
        if done is not None:
            stmt = stmt.where(models.Task.done == done)
        stmt = stmt.order_by(models.Task.priority, models.Task.id).limit(limit).offset(offset)
        return list(self.db.scalars(stmt))

    def save(self, task: models.Task) -> models.Task:
        self.db.add(task)
        self.db.commit()
        return task

    def delete(self, task: models.Task) -> None:
        self.db.delete(task)
        self.db.commit()
