from pathlib import Path

from strands.memory import MemoryManager
from strands.vended_memory_stores import FileMemoryStore


class ProjectSemanticMemory:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def create(self, project_name: str) -> MemoryManager:
        global_store = FileMemoryStore(
            name="factorie-global",
            storage_path=str(self.data_dir / "memories" / "global"),
        )

        project_store = FileMemoryStore(
            name=f"project-{project_name}",
            storage_path=str(self.data_dir / "memories" / "projects" / project_name),
        )

        return MemoryManager(
            stores=[
                global_store,
                project_store,
            ],
            search_tool_config=True,
            add_tool_config=True,
            injection=True,
        )
