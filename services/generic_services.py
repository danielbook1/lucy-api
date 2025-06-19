from typing import TypeVar, Generic, Type, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
PublicSchemaType = TypeVar("PublicSchemaType", bound=BaseModel)


class GenericServices(
    Generic[ModelType, CreateSchemaType, UpdateSchemaType, PublicSchemaType]
):
    def __init__(
        self,
        model: Type[ModelType],
    ):
        self.model = model

    async def fetch(self, obj_id: int, db: AsyncSession) -> ModelType | None:
        return await db.get(self.model, obj_id)

    async def fetch_all(self, db: AsyncSession) -> List[ModelType]:
        result = await db.execute(select(self.model))
        return result.scalars().all()

    async def build_model(self, schema: CreateSchemaType) -> ModelType:
        return self.model(**schema.model_dump())

    async def add_model(self, obj: ModelType, db: AsyncSession) -> ModelType:
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def update_model(
        self, schema: UpdateSchemaType, db_obj: ModelType, db: AsyncSession
    ) -> ModelType:
        updates = schema.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(db_obj, key, value)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete_model(self, db_obj: ModelType, db: AsyncSession):
        await db.delete(db_obj)
        await db.commit()
