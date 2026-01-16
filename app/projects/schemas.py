# clients/schemas.py
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class ProjectBase(BaseModel):
    name: str
    description: str | None = None
    completed: bool = False
    completed_on: datetime | None = None
    client_id: UUID | None = None
    deadline: datetime | None = None
    rate: float | None = None
    use_client_rate: bool = True
    hours_worked: float = 0
    use_task_hours: bool = True


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    completed: bool | None = None
    completed_on: datetime | None = None
    client_id: UUID | None = None
    deadline: datetime | None = None
    rate: float | None = None
    use_client_rate: bool | None = None
    hours_worked: float | None = None
    use_task_hours: bool | None = None


class ProjectRead(ProjectBase):
    id: UUID
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)


class TaskBase(BaseModel):
    name: str
    description: str | None = None
    project_id: UUID | None
    completed: bool = False
    completed_on: datetime | None = None
    deadline: datetime | None = None
    hours_worked: float = 0


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    project_id: UUID | None = None
    completed: bool | None = None
    completed_on: datetime | None = None
    deadline: datetime | None = None
    hours_worked: float | None = None


class TaskRead(TaskBase):
    id: UUID
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)
