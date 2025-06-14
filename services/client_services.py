from ..database.models.client import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ..database import db


async def fetch_client(client_id: int, db: AsyncSession):
    # Query clients
    return await db.get(Client, client_id)


async def fetch_all_clients(db: AsyncSession):
    # Query clients
    result = await db.execute(select(Client))
    return result.scalars().all()


async def build_client_model(client: ClientCreate):
    # Return model from schema
    return Client(**client.model_dump())


async def add_client_model(client: Client, db: AsyncSession):
    # Update database
    db.add(client)
    await db.commit()
    await db.refresh(client)


async def update_client_model(
    client: ClientUpdate, db_client: Client, db: AsyncSession
):
    # Get dicitonary of changes
    updates = client.model_dump(exclude_unset=True)

    # Update model attributes
    for key, value in updates.items():
        setattr(db_client, key, value)

    # Update database
    await db.commit()
    await db.refresh(db_client)


async def delete_client_model(client: Client, db: AsyncSession):
    # Update database
    await db.delete(client)
    await db.commit()
