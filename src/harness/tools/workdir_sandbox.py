import os
import shlex
import sys
from pathlib import Path
from typing import Any

from strands.sandbox.not_a_sandbox_local_environment import NotASandboxLocalEnvironment

# Entorno virtual del propio harness (p. ej. /home/.../Harness/.venv).
_HARNESS_VENV = Path(sys.prefix).resolve()

# Variables del entorno del harness que no deben filtrarse a los proyectos generados:
# harían que `uv run --active`, `pip`, `python` o `pytest` usen el venv del harness.
_LEAKY_VARS = ("VIRTUAL_ENV", "VIRTUAL_ENV_PROMPT", "UV_PROJECT_ENVIRONMENT", "PYTHONHOME", "CONDA_PREFIX")


def project_path() -> str:
    """PATH del host sin el ``bin/`` del venv del harness."""
    venv_bin = str(_HARNESS_VENV / "bin")
    parts = [p for p in os.environ.get("PATH", "").split(os.pathsep) if p and str(Path(p).resolve()) != venv_bin]
    return os.pathsep.join(parts)


def clean_env() -> dict[str, str]:
    """Copia del entorno del host apta para correr procesos del proyecto generado."""
    env = {k: v for k, v in os.environ.items() if k not in _LEAKY_VARS}
    env["PATH"] = project_path()
    return env


class WorkdirSandbox(NotASandboxLocalEnvironment):
    """Sandbox local (sin aislamiento) cuyo directorio de trabajo es el proyecto generado.

    Los built-ins del harness (shell, read, write, edit) resuelven rutas relativas y
    ejecutan comandos aquí, en lugar de en el cwd del proceso del harness, y sin heredar
    el entorno virtual del harness.
    """

    def __init__(self, workdir: Path, **kwargs: Any):
        super().__init__(**kwargs)
        self.workdir = str(Path(workdir).resolve())
        self._env_reset = (
            "unset " + " ".join(_LEAKY_VARS) + "\n"
            f"export PATH={shlex.quote(project_path())}\n"
        )

    def _resolve_path(self, path: str) -> Path:  # type: ignore[override]
        return Path(path if os.path.isabs(path) else os.path.join(self.workdir, path))

    async def execute_streaming(self, command, *, timeout=None, cwd=None, env=None, **kwargs):
        # El sandbox base ejecuta `cd <cwd> && <command>`. Si el comando tiene varias líneas o
        # un `&`, solo la primera parte queda dentro del `cd` y el resto corre en el cwd del
        # proceso (la raíz del harness). Agruparlo en `{ ...; }` mantiene todo en el workdir.
        grouped = "{\n" + self._env_reset + command + "\n}"
        async for chunk in super().execute_streaming(
            grouped, timeout=timeout, cwd=cwd or self.workdir, env=env, **kwargs
        ):
            yield chunk

    async def execute_code_streaming(self, code, language, *, timeout=None, cwd=None, env=None, **kwargs):
        async for chunk in super().execute_code_streaming(
            code, language, timeout=timeout, cwd=cwd or self.workdir, env=env, **kwargs
        ):
            yield chunk
