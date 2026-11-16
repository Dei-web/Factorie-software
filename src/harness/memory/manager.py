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

    def get_or_create_conversation(
        self, conversation_key: str, project_name: str, workdir: str
    ) -> tuple[ExecutionMemory, bool]:
        """Devuelve la ejecución activa de una conversación, o crea una nueva.

        El segundo valor indica si la ejecución es nueva.
        """
        execution_id = self.repository.get_conversation(conversation_key)

        if execution_id is not None:
            execution = self.repository.get(execution_id)
            if execution is not None:
                return execution, False

        execution = self.create_execution(project_name=project_name, workdir=workdir)
        self.repository.set_conversation(conversation_key, execution.execution_id)
        return execution, True

    def reset_conversation(self, conversation_key: str):
        self.repository.delete_conversation(conversation_key)

    def get_execution(self, execution_id: str):
        return self.repository.get(execution_id)

    def save_execution(self, execution: ExecutionMemory):
        self.repository.save(execution)
