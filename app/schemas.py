from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProjectIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=2000)

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name must not be blank")
        return v


class ProjectOut(ProjectIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    task_count: int = 0


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    done: bool = False
    priority: int = Field(default=2, ge=1, le=3)

    @field_validator("title")
    @classmethod
    def strip_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("title must not be blank")
        return v


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    done: bool | None = None
    priority: int | None = Field(default=None, ge=1, le=3)


class TaskOut(TaskIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
