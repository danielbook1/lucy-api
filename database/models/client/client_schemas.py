from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from . import Client


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
    # projects: List[int]

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def serialize(cls, client: Client):
        return cls.model_validate(client)
