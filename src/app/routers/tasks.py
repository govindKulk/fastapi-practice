from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.task import task as crud_task
from app.models.task import TaskCreate, TaskUpdate, TaskResponse, TaskPriority, TaskStatus
from app.models.database import User
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[TaskResponse])
async def read_tasks(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = Query(default=100, le=100),
    priority: Optional[TaskPriority] = None,
    status: Optional[TaskStatus] = None,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """Retrieve tasks."""
    tasks = await crud_task.get_tasks_by_owner(
        db, owner_id=int(current_user.id),  # type: ignore[arg-type]
        skip=skip, limit=limit,
        priority=priority, status=status
    )
    return tasks

@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    *,
    db: AsyncSession = Depends(deps.get_db),
    task_in: TaskCreate,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """Create new task."""
    task = await crud_task.create_with_owner(
        db, obj_in=task_in, owner_id=int(current_user.id)  # type: ignore[arg-type]
    )
    return task

@router.get("/{id}", response_model=TaskResponse)
async def read_task(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """Get task by ID."""
    task = await crud_task.get(db, id=id)
   
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if int(task.owner_id) != int(current_user.id):  # type: ignore[arg-type]
        raise HTTPException(status_code=403, detail="Not authorized to access this task")
    
    return task

@router.put("/{id}", response_model=TaskResponse)
async def update_task(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """Update a task."""
    task = await crud_task.get(db, id=id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if int(task.owner_id) != int(current_user.id):  # type: ignore[arg-type]
        raise HTTPException(status_code=403, detail="Not authorized to update this task")
    
    task = await crud_task.update(db, db_obj=task, obj_in=task_in)
    return task

@router.delete("/{id}")
async def delete_task(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """Delete a task."""
    task = await crud_task.get(db, id=id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if int(task.owner_id) != int(current_user.id):  # type: ignore[arg-type]
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")
    
    await crud_task.remove(db, id=id)
    return {"message": "Task deleted successfully"}
