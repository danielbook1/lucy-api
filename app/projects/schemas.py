# clients/schemas.py
from pydantic import BaseModel, ConfigDict
from uuid import UUID


class ProjectBase(BaseModel):
    name: str
    client_id: UUID


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = None
    client_id: UUID | None = None


class ProjectRead(ProjectBase):
    id: UUID
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)
