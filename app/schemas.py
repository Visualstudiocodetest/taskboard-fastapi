"""Request/response models. Shared constrained types keep the rules in one place."""
from dataclasses import dataclass
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


def _text(max_length: int):
    # Trimmed, non-blank string: "   " is rejected after stripping.
    return Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=max_length)
    ]


Name = _text(100)
Title = _text(200)
Priority = Annotated[int, Field(ge=1, le=3)]  # 1 = high, 2 = normal, 3 = low


@dataclass
class Page:
    """Pagination window shared by all list endpoints."""

    limit: int = 100
    offset: int = 0


class ProjectIn(BaseModel):
    name: Name
    description: str | None = Field(default=None, max_length=2000)


class ProjectOut(ProjectIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    task_count: int = 0


class TaskIn(BaseModel):
    title: Title
    done: bool = False
    priority: Priority = 2


class TaskUpdate(BaseModel):
    """PATCH body: every field optional, only the ones sent are applied."""

    title: Title | None = None
    done: bool | None = None
    priority: Priority | None = None


class TaskOut(TaskIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
