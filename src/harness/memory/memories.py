from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskMemory(BaseModel):
    task_id: str
    agent: str
    status: TaskStatus = TaskStatus.PENDING
    attempts: int = 0
    result: str | None = None
    error: str | None = None
    dependencies: list[str] = Field(default_factory=list)


class ExecutionMemory(BaseModel):
    execution_id: str
    project_name: str
    workdir: str
    current_phase: str
    tasks: list[TaskMemory] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
