import os
from pathlib import Path
from typing import Any

from strands.sandbox.not_a_sandbox_local_environment import NotASandboxLocalEnvironment


class WorkdirSandbox(NotASandboxLocalEnvironment):
    """Sandbox local (sin aislamiento) cuyo directorio de trabajo es el proyecto generado.

    Los built-ins del harness (shell, read, write, edit) resuelven rutas relativas y
    ejecutan comandos aquí, en lugar de en el cwd del proceso del harness.
    """

    def __init__(self, workdir: Path, **kwargs: Any):
        super().__init__(**kwargs)
        self.workdir = str(Path(workdir).resolve())

    def _resolve_path(self, path: str) -> Path:  # type: ignore[override]
        return Path(path if os.path.isabs(path) else os.path.join(self.workdir, path))

    async def execute_streaming(self, command, *, timeout=None, cwd=None, env=None, **kwargs):
        async for chunk in super().execute_streaming(
            command, timeout=timeout, cwd=cwd or self.workdir, env=env, **kwargs
        ):
            yield chunk

    async def execute_code_streaming(self, code, language, *, timeout=None, cwd=None, env=None, **kwargs):
        async for chunk in super().execute_code_streaming(
            code, language, timeout=timeout, cwd=cwd or self.workdir, env=env, **kwargs
        ):
            yield chunk
