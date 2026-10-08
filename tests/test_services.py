"""Service tests with an in-memory fake repository: no database needed (DIP)."""
import pytest

from app import models, schemas
from app.exceptions import NotFoundError, ValidationError
from app.services import TaskService


class FakeProjects:
    def get(self, project_id):
        return models.Project(id=1, name="p") if project_id == 1 else None


class FakeTasks:
    def __init__(self):
        self.saved = []

    def get(self, task_id):
        return models.Task(id=task_id, title="t", done=False, priority=2, project_id=1)

    def save(self, task):
        self.saved.append(task)
        return task


@pytest.fixture()
def service():
    return TaskService(FakeTasks(), FakeProjects())


def test_create_task_requires_existing_project(service):
    with pytest.raises(NotFoundError):
        service.create(42, schemas.TaskIn(title="x"))


def test_update_rejects_null_value(service):
    with pytest.raises(ValidationError):
        service.update(1, schemas.TaskUpdate(title=None))


def test_update_applies_only_given_fields(service):
    task = service.update(1, schemas.TaskUpdate(done=True))
    assert task.done is True and task.title == "t"
