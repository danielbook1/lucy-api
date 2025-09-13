# clients/schemas.py
from pydantic import BaseModel, ConfigDict
from uuid import UUID


class ClientBase(BaseModel):
    name: str


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: str | None = None


class ClientRead(ClientBase):
    id: UUID
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)
