"""Business rules. Depends on repositories, knows nothing about HTTP or SQL."""
from . import models, schemas
from .exceptions import NotFoundError, ValidationError
from .repositories import ProjectRepository, TaskRepository


def _require(entity, label: str, entity_id: int):
    """Return the entity or raise NotFoundError (shared by every service)."""
    if entity is None:
        raise NotFoundError(f"{label} {entity_id} not found")
    return entity


def _apply(entity, values: dict) -> None:
    for key, value in values.items():
        setattr(entity, key, value)


class ProjectService:
    def __init__(self, projects: ProjectRepository):
        self.projects = projects

    def _get(self, project_id: int) -> models.Project:
        return _require(self.projects.get(project_id), "Project", project_id)

    @staticmethod
    def _out(project: models.Project, task_count: int) -> schemas.ProjectOut:
        return schemas.ProjectOut(
            id=project.id,
            name=project.name,
            description=project.description,
            task_count=task_count,
        )

    def list(self, page: schemas.Page) -> list[schemas.ProjectOut]:
        return [self._out(p, c) for p, c in self.projects.list_with_counts(page)]

    def get(self, project_id: int) -> schemas.ProjectOut:
        project = self._get(project_id)
        return self._out(project, self.projects.count_tasks(project_id))

    def create(self, data: schemas.ProjectIn) -> schemas.ProjectOut:
        project = self.projects.save(models.Project(**data.model_dump()))
        return self._out(project, 0)

    def update(self, project_id: int, data: schemas.ProjectIn) -> schemas.ProjectOut:
        project = self._get(project_id)
        _apply(project, data.model_dump())
        self.projects.save(project)
        return self._out(project, self.projects.count_tasks(project_id))

    def delete(self, project_id: int) -> None:
        self.projects.delete(self._get(project_id))


class TaskService:
    def __init__(self, tasks: TaskRepository, projects: ProjectRepository):
        self.tasks = tasks
        self.projects = projects

    def _get(self, task_id: int) -> models.Task:
        return _require(self.tasks.get(task_id), "Task", task_id)

    def _ensure_project(self, project_id: int) -> None:
        _require(self.projects.get(project_id), "Project", project_id)

    def list(self, project_id: int, done: bool | None, page: schemas.Page):
        self._ensure_project(project_id)
        return self.tasks.list_for_project(project_id, done, page)

    def create(self, project_id: int, data: schemas.TaskIn) -> models.Task:
        self._ensure_project(project_id)
        return self.tasks.save(models.Task(project_id=project_id, **data.model_dump()))

    def update(self, task_id: int, data: schemas.TaskUpdate) -> models.Task:
        task = self._get(task_id)
        changes = data.model_dump(exclude_unset=True)  # only fields the client sent
        for key, value in changes.items():
            if value is None:  # explicit null is not allowed on these columns
                raise ValidationError(f"{key} cannot be null")
        _apply(task, changes)
        return self.tasks.save(task)

    def delete(self, task_id: int) -> None:
        self.tasks.delete(self._get(task_id))
