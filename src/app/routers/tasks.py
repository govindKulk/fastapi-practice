from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.task import task as crud_task
from app.models.task import TaskCreate, TaskUpdate, TaskResponse, TaskPriority, TaskStatus
from app.core.database import get_db

router = APIRouter()

@router.get("/", response_model=List[TaskResponse])
async def read_tasks(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = Query(default=100, le=100),
    priority: Optional[TaskPriority] = None,
    status: Optional[TaskStatus] = None,
    current_user: int = 1  # We'll implement authentication tomorrow
) -> Any:
    """Retrieve tasks."""
    tasks = await crud_task.get_tasks_by_owner(
        db, owner_id=current_user, skip=skip, limit=limit,
        priority=priority, status=status
    )
    return tasks

@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    *,
    db: AsyncSession = Depends(get_db),
    task_in: TaskCreate,
    current_user: int = 1  # We'll implement authentication tomorrow
) -> Any:
    """Create new task."""
    task = await crud_task.create_with_owner(
        db, obj_in=task_in, owner_id=current_user
    )
    return task

@router.get("/{id}", response_model=TaskResponse)
async def read_task(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: int = 1  # We'll implement authentication tomorrow
) -> Any:
    """Get task by ID."""
    task = await crud_task.get(db, id=id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{id}", response_model=TaskResponse)
async def update_task(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    task_in: TaskUpdate,
    current_user: int = 1  # We'll implement authentication tomorrow
) -> Any:
    """Update a task."""
    task = await crud_task.get(db, id=id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task = await crud_task.update(db, db_obj=task, obj_in=task_in)
    return task

@router.delete("/{id}")
async def delete_task(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: int = 1  # We'll implement authentication tomorrow
) -> Any:
    """Delete a task."""
    task = await crud_task.get(db, id=id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await crud_task.remove(db, id=id)
    return {"message": "Task deleted successfully"}
