from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from . import Task


class TaskBase(BaseModel):
    # Identification
    name: str
    description: str

    # Status
    start_date: datetime
    deadline: Optional[datetime] = None
    is_complete: bool = False

    # Metrics
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None

    # Project
    project_id: int


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    # Identification
    name: Optional[str] = None
    description: Optional[str] = None

    # Status
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    is_complete: Optional[bool] = None

    # Metrics
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None

    # Project
    project_id: Optional[int] = None


class TaskPublic(TaskBase):
    # Identification
    id: int

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def serialize(cls, task: Task):
        return cls.model_validate(task)
