import re
import unicodedata
from pathlib import Path
from uuid import uuid4

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

_STOPWORDS = {
    "a", "al", "con", "crea", "creame", "de", "del", "el", "en", "haz", "la", "las", "lo",
    "los", "me", "para", "por", "que", "quiero", "sobre", "un", "una", "uno", "y",
}


def project_slug(description: str, max_words: int = 4) -> str:
    """Nombre de carpeta legible a partir de la tarea: 'web-inteligencia-artificial-a1b2'."""
    text = unicodedata.normalize("NFKD", description).encode("ascii", "ignore").decode().lower()
    words = [w for w in re.findall(r"[a-z0-9]+", text) if w not in _STOPWORDS]
    base = "-".join(words[:max_words]) or "proyecto"
    return f"{base}-{uuid4().hex[:4]}"


def safe_project_name(name: str) -> str:
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", name.strip()).strip("-.")
    if not name:
        raise ValueError("Nombre de proyecto vacío o inválido.")
    return name


def create_application(
    conversation_key: str,
    description: str = "",
    project_name: str | None = None,
):
    """Crea (o retoma) el agente de una conversación.

    - Conversación existente: retoma su ejecución, su sesión (historial) y su proyecto.
    - Conversación nueva: usa ``project_name`` si se fijó con /proyecto; si no, crea una
      carpeta nueva en ``generated_projects/`` nombrada a partir de la tarea.
    """
    execution = memory_manager.get_conversation(conversation_key)
    is_new = execution is None

    if is_new:
        name = safe_project_name(project_name) if project_name else project_slug(description)
        workdir = GENERATED_PROJECTS_DIR / name
        execution = memory_manager.start_conversation(
            conversation_key=conversation_key,
            project_name=name,
            workdir=str(workdir),
        )

    workdir = Path(execution.workdir)
    workdir.mkdir(parents=True, exist_ok=True)

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
