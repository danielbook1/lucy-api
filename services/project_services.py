from ..database.models.project import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def fetch_project(project_id: int, db: AsyncSession):
    # Query projects
    return await db.get(Project, project_id)


async def fetch_all_projects(db: AsyncSession):
    # Query projects
    result = await db.execute(select(Project))
    return result.scalars().all()


async def build_project_model(project: ProjectCreate):
    # Return model from schema
    return Project(**project.model_dump())


async def add_project_model(project: Project, db: AsyncSession):
    # Update database
    db.add(project)
    await db.commit()
    await db.refresh(project)


async def update_project_model(
    project: ProjectUpdate, db_project: Project, db: AsyncSession
):
    # Get dicitonary of changes
    updates = project.model_dump(exclude_unset=True)

    # Update model attributes
    for key, value in updates.items():
        setattr(db_project, key, value)

    # Update database
    await db.commit()
    await db.refresh(db_project)


async def delete_project_model(project: Project, db: AsyncSession):
    # Update database
    await db.delete(project)
    await db.commit()
