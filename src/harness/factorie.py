from pathlib import Path

from strands.session import SnapshotSessionManager
from strands.storage import LocalFileStorage

from harness.agents.orchester import create_orchestrator
from harness.config.settings import GENERATED_PROJECTS_DIR
from harness.memory.manager import MemoryManager

PROJECT_ROOT = Path(__file__).resolve().parents[2]

memory_manager = MemoryManager(PROJECT_ROOT / "data" / "harness.db")

session_storage = LocalFileStorage(
    base_dir=str(PROJECT_ROOT / "data" / "strands_sessions")
)


def create_application(project_name: str, conversation_key: str):
    """Crea (o retoma) el agente de una conversación.

    La misma ``conversation_key`` reutiliza la misma ejecución y la misma sesión de
    Strands, que restaura automáticamente el historial guardado en disco.
    """
    workdir = GENERATED_PROJECTS_DIR / project_name
    workdir.mkdir(parents=True, exist_ok=True)

    execution, is_new = memory_manager.get_or_create_conversation(
        conversation_key=conversation_key,
        project_name=project_name,
        workdir=str(workdir),
    )

    session_manager = SnapshotSessionManager(
        session_id=execution.execution_id,
        storage=session_storage,
        save_latest_on="message",
    )

    agent = create_orchestrator(
        session_manager=session_manager,
        workdir=workdir,
        storage=session_storage,
    )

    return agent, workdir, execution, is_new
