"""Business rules. Depends on repositories, knows nothing about HTTP or SQL."""
from . import models, schemas
from .exceptions import NotFoundError, ValidationError
from .repositories import ProjectRepository, TaskRepository


class ProjectService:
    def __init__(self, projects: ProjectRepository):
        self.projects = projects

    def _get(self, project_id: int) -> models.Project:
        project = self.projects.get(project_id)
        if project is None:
            raise NotFoundError(f"Project {project_id} not found")
        return project

    def _out(self, project: models.Project, task_count: int) -> schemas.ProjectOut:
        return schemas.ProjectOut(
            id=project.id,
            name=project.name,
            description=project.description,
            task_count=task_count,
        )

    def list(self, limit: int, offset: int) -> list[schemas.ProjectOut]:
        return [self._out(p, c) for p, c in self.projects.list_with_counts(limit, offset)]

    def get(self, project_id: int) -> schemas.ProjectOut:
        project = self._get(project_id)
        return self._out(project, self.projects.count_tasks(project_id))

    def create(self, data: schemas.ProjectIn) -> schemas.ProjectOut:
        project = self.projects.save(models.Project(**data.model_dump()))
        return self._out(project, 0)

    def update(self, project_id: int, data: schemas.ProjectIn) -> schemas.ProjectOut:
        project = self._get(project_id)
        for key, value in data.model_dump().items():
            setattr(project, key, value)
        self.projects.save(project)
        return self._out(project, self.projects.count_tasks(project_id))

    def delete(self, project_id: int) -> None:
        self.projects.delete(self._get(project_id))


class TaskService:
    def __init__(self, tasks: TaskRepository, projects: ProjectRepository):
        self.tasks = tasks
        self.projects = projects

    def _get(self, task_id: int) -> models.Task:
        task = self.tasks.get(task_id)
        if task is None:
            raise NotFoundError(f"Task {task_id} not found")
        return task

    def _ensure_project(self, project_id: int) -> None:
        if self.projects.get(project_id) is None:
            raise NotFoundError(f"Project {project_id} not found")

    def list(self, project_id: int, done: bool | None, limit: int, offset: int):
        self._ensure_project(project_id)
        return self.tasks.list_for_project(project_id, done, limit, offset)

    def create(self, project_id: int, data: schemas.TaskIn) -> models.Task:
        self._ensure_project(project_id)
        return self.tasks.save(models.Task(project_id=project_id, **data.model_dump()))

    def update(self, task_id: int, data: schemas.TaskUpdate) -> models.Task:
        task = self._get(task_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            if value is None:
                raise ValidationError(f"{key} cannot be null")
            setattr(task, key, value)
        return self.tasks.save(task)

    def delete(self, task_id: int) -> None:
        self.tasks.delete(self._get(task_id))
