from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.crud.base import CRUDBase
from app.models.database import Task
from app.models.task import TaskCreate, TaskUpdate, TaskPriority, TaskStatus

class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    async def get_tasks_by_owner(
        self,
        db: AsyncSession,
        *,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
        priority: Optional[TaskPriority] = None,
        status: Optional[TaskStatus] = None
    ) -> Sequence[Task]:
        query = select(Task).where(Task.owner_id == owner_id)

        if priority:
            query = query.where(Task.priority == priority)
        if status:
            query = query.where(Task.status == status)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: TaskCreate, owner_id: int
    ) -> Task:
        obj_in_data = obj_in.model_dump()
        db_obj = Task(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

task = CRUDTask(Task)
