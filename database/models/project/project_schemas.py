from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from . import Project
from ..task import TaskPublic


class ProjectBase(BaseModel):
    # Identification
    name: str
    description: str
    tags: List[str] = []

    # Status
    start_date: datetime
    deadline: Optional[datetime] = None
    is_complete: bool = False

    # Client
    client_id: int


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    # Identification
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None

    # Status
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    is_complete: bool = False

    # Client
    client_id: Optional[int] = None

    # Tasks


class ProjectPublic(ProjectBase):
    # Identification
    id: int

    # Tasks
    tasks: List[TaskPublic]

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def serialize(cls, project: Project):
        return cls.model_validate(project)
