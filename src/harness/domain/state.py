from pydantic import BaseModel


class TaskRequest(BaseModel):
    description: str
    source: str


class TaskResult(BaseModel):
    execution_id: str
    response: str
    interrupted: bool = False
    interrupt_id: str | None = None
