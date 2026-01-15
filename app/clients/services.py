from uuid import UUID

from sqlalchemy import select
from app.clients.models import Client
from app.clients.schemas import ClientCreate, ClientUpdate
from app.projects.models import Project
from sqlalchemy.ext.asyncio import AsyncSession


async def create_client(db: AsyncSession, client_in: ClientCreate, user_id: UUID):
    client = Client(**client_in.model_dump(), user_id=user_id)
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client


async def read_client(db: AsyncSession, client_id: UUID):
    result = await db.get(Client, client_id)
    return result


async def read_clients(db: AsyncSession, user_id: UUID):
    result = await db.execute(select(Client).where(Client.user_id == user_id))
    clients = result.scalars().all()
    return clients


async def update_client(db: AsyncSession, client: Client, client_in: ClientUpdate):
    for field, value in client_in.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client


async def delete_client(db: AsyncSession, client: Client):
    # Set client_id to None for all projects associated with this client
    result = await db.execute(
        select(Project).where(Project.client_id == client.id)
    )
    projects = result.scalars().all()
    for project in projects:
        project.client_id = None
        db.add(project)
    
    await db.delete(client)
    await db.commit()
    return client
