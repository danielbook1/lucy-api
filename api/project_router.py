from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..database.models.project import *
from ..services.project_services import project_services

project_router = APIRouter(prefix="/project", tags=["project"])


@project_router.post("/", response_model=ProjectPublic)
async def create_project(project: ProjectCreate, db: AsyncSession = Depends(get_db)):
    # Create new project model
    db_project = await project_services.build_model(project)

    # Add model to database
    await project_services.add_model(db_project, db)

    # Return new model
    return ProjectPublic.serialize(db_project)


@project_router.get("/", response_model=list[ProjectPublic])
async def read_projects(db: AsyncSession = Depends(get_db)):
    # Query database
    projects = await project_services.fetch_all(db)

    # Return ProjectPublic schemas
    return [ProjectPublic.serialize(project) for project in projects]


@project_router.get("/{project_id}", response_model=ProjectPublic)
async def read_project(project_id: int, db: AsyncSession = Depends(get_db)):
    # Query database
    project = await project_services.fetch(project_id, db)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Return ProjectPublic schema
    return ProjectPublic.serialize(project)


@project_router.patch("/{project_id}", response_model=ProjectPublic)
async def update_project(
    project_id: int, project: ProjectUpdate, db: AsyncSession = Depends(get_db)
):
    # Query database
    db_project = await project_services.fetch(project_id, db)

    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Update project in database
    await project_services.update_model(project, db_project, db)

    # Return updated model
    return ProjectPublic.serialize(db_project)


@project_router.delete("/{project_id}")
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    # Query database
    project = await project_services.fetch(project_id, db)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Delete project from database
    await project_services.delete_model(project, db)

    # Return success
    return {"ok": True}
