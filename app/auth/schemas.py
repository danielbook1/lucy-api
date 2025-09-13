from typing import List, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict
from uuid import UUID


if TYPE_CHECKING:
    from app.clients.schemas import ClientRead


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class UserWithClients(UserRead):
    clients: List["ClientRead"] = []


class UserInDB(UserBase):
    id: UUID
    hashed_password: str

    model_config = ConfigDict(from_attributes=True)
