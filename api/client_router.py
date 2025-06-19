from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..database.models.client import *
from ..services.client_services import client_services

client_router = APIRouter(prefix="/client", tags=["client"])


@client_router.post("/", response_model=ClientPublic)
async def create_client(client: ClientCreate, db: AsyncSession = Depends(get_db)):
    # Create new client model
    db_client = await client_services.build_model(client)

    # Add model to database
    await client_services.add_model(db_client, db)

    # Return new model
    return ClientPublic.serialize(db_client)


@client_router.get("/", response_model=list[ClientPublic])
async def read_clients(db: AsyncSession = Depends(get_db)):
    # Query database
    clients = await client_services.fetch_all(db)

    # Return ClientPublic schemas
    return [ClientPublic.serialize(client) for client in clients]


@client_router.get("/{client_id}", response_model=ClientPublic)
async def read_client(client_id: int, db: AsyncSession = Depends(get_db)):
    # Query database
    client = await client_services.fetch(client_id, db)

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Return ClientPublic schema
    return ClientPublic.serialize(client)


@client_router.patch("/{client_id}", response_model=ClientPublic)
async def update_client(
    client_id: int, client: ClientUpdate, db: AsyncSession = Depends(get_db)
):
    # Query database
    db_client = await client_services.fetch(client_id, db)

    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Update client in database
    await client_services.update_model(client, db_client, db)

    # Return updated model
    return ClientPublic.serialize(db_client)


@client_router.delete("/{client_id}")
async def delete_client(client_id: int, db: AsyncSession = Depends(get_db)):
    # Query database
    client = await client_services.fetch(client_id, db)

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Delete client from database
    await client_services.delete_model(client, db)

    # Return success
    return {"ok": True}
