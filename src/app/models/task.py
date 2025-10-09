from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from enum import Enum
from datetime import datetime

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskBase(BaseModel):
    title: str = Field(..., description="Title of the task", max_length=100)
    description: Optional[str] = Field(None, description="Task Description", max_length=500)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Priority of the task")
    due_date: Optional[datetime] = Field(None, description="Due date of the task")

class TaskCreate(TaskBase):
    """Model for creating a new task"""
    pass

class TaskUpdate(BaseModel):
    """Model for updating an existing task - all fields optional"""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None

class TaskResponse(TaskBase):
    """Model for task responses"""
    id: int
    status: TaskStatus = TaskStatus.PENDING
    
    model_config = ConfigDict(from_attributes=True)

class TaskListResponse(BaseModel):
    """Model for paginated task list response"""
    tasks: List[TaskResponse]
    total: int
    page: int
    per_page: int
