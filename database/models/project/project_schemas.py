from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from . import Project


class ProjectBase(BaseModel):
    # Identification
    description: str
    tags: List[str] = []

    # Dates
    start_date: datetime
    deadline: Optional[datetime] = None

    # Client

    # Tasks


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    # Identification
    description: Optional[str] = None
    tags: Optional[List[str]] = None

    # Dates
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None

    # Client

    # Tasks


class ProjectPublic(ProjectBase):
    # Identification
    id: int

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def serialize(cls, project: Project):
        return cls.model_validate(project)
