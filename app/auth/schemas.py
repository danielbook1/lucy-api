from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserBase):
    id: UUID
    hashed_password: str

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
