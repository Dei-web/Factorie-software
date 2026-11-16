from pathlib import Path
from uuid import uuid4

from harness.memory.memories import ExecutionMemory
from harness.memory.repository import MemoryRepository


class MemoryManager:
    def __init__(self, database_path: Path):
        self.repository = MemoryRepository(database_path)

    def create_execution(self, project_name: str, workdir: str) -> ExecutionMemory:

        execution = ExecutionMemory(
            execution_id=str(uuid4()),
            project_name=project_name,
            workdir=workdir,
            current_phase="spec_writer",
        )

        self.repository.save(execution)
        return execution

    def get_conversation(self, conversation_key: str) -> ExecutionMemory | None:
        """Ejecución activa de una conversación, o ``None`` si no hay ninguna."""
        execution_id = self.repository.get_conversation(conversation_key)
        return None if execution_id is None else self.repository.get(execution_id)

    def start_conversation(
        self, conversation_key: str, project_name: str, workdir: str
    ) -> ExecutionMemory:
        execution = self.create_execution(project_name=project_name, workdir=workdir)
        self.repository.set_conversation(conversation_key, execution.execution_id)
        return execution

    def reset_conversation(self, conversation_key: str):
        self.repository.delete_conversation(conversation_key)

    def get_execution(self, execution_id: str):
        return self.repository.get(execution_id)

    def save_execution(self, execution: ExecutionMemory):
        self.repository.save(execution)
