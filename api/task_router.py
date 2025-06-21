from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..database.models.task import *
from ..services.task_services import task_services

task_router = APIRouter(prefix="/task", tags=["task"])


@task_router.post("", response_model=TaskPublic)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    # Create new task model
    db_task = await task_services.build_model(task)

    # Add model to database
    await task_services.add_model(db_task, db)

    # Return new model
    return TaskPublic.serialize(db_task)


@task_router.get("", response_model=list[TaskPublic])
async def read_task(db: AsyncSession = Depends(get_db)):
    # Query database
    tasks = await task_services.fetch_all(db)

    # Return TaskPublic schemas
    return [TaskPublic.serialize(task) for task in tasks]


@task_router.get("/{task_id}", response_model=TaskPublic)
async def read_task(task_id: int, db: AsyncSession = Depends(get_db)):
    # Query database
    task = await task_services.fetch(task_id, db)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Return TaskPublic schema
    return TaskPublic.serialize(task)


@task_router.patch("/{task_id}", response_model=TaskPublic)
async def update_task(
    task_id: int, task: TaskUpdate, db: AsyncSession = Depends(get_db)
):
    # Query database
    db_task = await task_services.fetch(task_id, db)

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update task in database
    await task_services.update_model(task, db_task, db)

    # Return updated model
    return TaskPublic.serialize(db_task)


@task_router.delete("/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    # Query database
    task = await task_services.fetch(task_id, db)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Delete task from database
    await task_services.delete_model(task, db)

    # Return success
    return {"ok": True}
