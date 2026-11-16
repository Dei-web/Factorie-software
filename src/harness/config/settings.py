from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

GENERATED_PROJECTS_DIR = PROJECT_ROOT / "generated_projects"
GENERATED_PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
