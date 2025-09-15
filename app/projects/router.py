from click import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.models import User
from app.projects.schemas import ProjectCreate, ProjectRead, ProjectUpdate
from app.projects.services import (
    create_project,
    read_project,
    read_projects,
    read_client_projects,
    update_project,
    delete_project,
)
from app.database import get_db
from app.auth.services import get_current_user

router = APIRouter()


@router.post("/", response_model=ProjectRead)
async def new_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = await create_project(db, project_in, user_id=current_user.id)
    return project


@router.get("/get/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = await read_project(db, UUID(project_id))
    if project is None or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/client/{client_id}", response_model=list[ProjectRead])
async def list_client_projects(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    projects = await read_client_projects(
        db, client_id=UUID(client_id), user_id=current_user.id
    )
    return projects


@router.get("/all/", response_model=list[ProjectRead])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    projects = await read_projects(db, user_id=current_user.id)
    return projects


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project_endpoint(
    project_id: str,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = await read_project(db, UUID(project_id))
    if project is None or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    project = await update_project(db, project, project_in)
    return project


@router.delete("/{project_id}", response_model=ProjectRead)
async def delete_project_endpoint(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = await read_project(db, UUID(project_id))
    if project is None or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    project = await delete_project(db, project)
    return project
