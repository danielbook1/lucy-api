from uuid import UUID

from sqlalchemy import select
from app.projects.models import Project, Task
from app.clients.models import Client
from app.projects.schemas import ProjectCreate, ProjectUpdate, TaskCreate, TaskUpdate
from sqlalchemy.ext.asyncio import AsyncSession


async def create_project(db: AsyncSession, project_in: ProjectCreate, user_id: UUID):
    project = Project(**project_in.model_dump(), user_id=user_id)
    
    # If project has a client_id but no rate, inherit rate from client
    if project.client_id and project.rate is None:
        client = await db.get(Client, project.client_id)
        if client:
            project.rate = client.rate
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def read_project(db: AsyncSession, project_id: UUID):
    result = await db.get(Project, project_id)
    return result


async def read_projects(db: AsyncSession, user_id: UUID):
    result = await db.execute(select(Project).where(Project.user_id == user_id))
    projects = result.scalars().all()
    return projects


async def read_client_projects(db: AsyncSession, client_id: UUID | None, user_id: UUID):
    result = await db.execute(
        select(Project).where(
            Project.client_id == client_id,
            Project.user_id == user_id,
        )
    )
    projects = result.scalars().all()
    return projects


async def update_project(db: AsyncSession, project: Project, project_in: ProjectUpdate):
    # Check if client_id is being updated
    update_data = project_in.model_dump(exclude_unset=True)
    
    # If client_id is being set/changed and rate is not being explicitly set
    if "client_id" in update_data and "rate" not in update_data:
        client_id = update_data["client_id"]
        if client_id and project.rate is None:
            # Inherit rate from the new client if current project rate is None
            client = await db.get(Client, client_id)
            if client:
                update_data["rate"] = client.rate
    
    for field, value in update_data.items():
        setattr(project, field, value)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def delete_project(db: AsyncSession, project: Project):
    await db.delete(project)
    await db.commit()
    return project


async def create_task(db: AsyncSession, task_in: TaskCreate, user_id: UUID):
    task = Task(**task_in.model_dump(), user_id=user_id)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def read_task(db: AsyncSession, task_id: UUID):
    result = await db.get(Task, task_id)
    return result


async def read_project_tasks(db: AsyncSession, project_id: UUID, user_id: UUID):
    result = await db.execute(
        select(Task).where(
            Task.project_id == project_id,
            Task.user_id == user_id,
        )
    )
    tasks = result.scalars().all()
    return tasks


async def read_user_tasks(db: AsyncSession, user_id: UUID):
    result = await db.execute(
        select(Task).where(Task.user_id == user_id)
    )
    tasks = result.scalars().all()
    return tasks


async def update_task(db: AsyncSession, task: Task, task_in: TaskUpdate):
    for field, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task: Task):
    await db.delete(task)
    await db.commit()
    return task
