from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from . import Client
from ..project import ProjectPublic


class ClientBase(BaseModel):
    # Identification
    name: str


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    # Identification
    name: Optional[str] = None


class ClientPublic(ClientBase):
    # Identification
    id: int

    # Projects
    projects: List[ProjectPublic]

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def serialize(cls, client: Client):
        return cls.model_validate(client)
