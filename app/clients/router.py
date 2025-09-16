from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.models import User
from app.clients.schemas import ClientCreate, ClientRead, ClientUpdate
from app.clients.services import (
    create_client,
    read_client,
    read_clients,
    update_client,
    delete_client,
)
from app.database import get_db
from app.auth.services import get_current_user

router = APIRouter()


@router.post("/", response_model=ClientRead)
async def new_client(
    client_in: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = await create_client(db, client_in, user_id=current_user.id)
    return client


@router.get("/get/{client_id}", response_model=ClientRead)
async def get_client(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = await read_client(db, UUID(client_id))
    if client is None or client.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.get("/all/", response_model=list[ClientRead])
async def list_clients(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    clients = await read_clients(db, user_id=current_user.id)
    return clients


@router.patch("/{client_id}", response_model=ClientRead)
async def update_client_endpoint(
    client_id: str,
    client_in: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = await read_client(db, UUID(client_id))
    if client is None or client.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Client not found")
    client = await update_client(db, client, client_in)
    return client


@router.delete("/{client_id}", response_model=ClientRead)
async def delete_client_endpoint(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = await read_client(db, UUID(client_id))
    if client is None or client.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Client not found")
    client = await delete_client(db, client)
    return client
