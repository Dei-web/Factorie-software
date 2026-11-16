import os
import signal
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from strands import tool

from harness.tools.workdir_sandbox import clean_env

_MAX_BODY = 1500


def _fetch(url: str, timeout: float = 5.0) -> tuple[int | None, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310 (solo localhost)
            return resp.status, resp.read(_MAX_BODY).decode("utf-8", "replace")
    except urllib.error.HTTPError as err:
        return err.code, err.read(_MAX_BODY).decode("utf-8", "replace")
    except Exception as err:  # conexión rechazada, timeout, etc.
        return None, f"{type(err).__name__}: {err}"


def make_server_check_tool(workdir: Path):
    workdir = Path(workdir).resolve()

    @tool
    def server_check(command: str, port: int, paths: list[str] | None = None, startup_timeout: int = 30) -> str:
        """Arranca un servidor, espera a que responda, hace peticiones GET y SIEMPRE lo detiene.

        Es la ÚNICA forma correcta de verificar que un servidor (uvicorn, flask, npm run dev,
        http.server...) levanta y responde. Nunca lances servidores con `&` desde `shell`:
        quedan colgados y bloquean la herramienta.

        Args:
            command: Comando que arranca el servidor en primer plano, p. ej.
                "uv run uvicorn src.main:app --port 8010". Se ejecuta en el directorio del proyecto.
            port: Puerto en el que escucha (en 127.0.0.1). Elige uno poco común (8010-8099).
            paths: Rutas a pedir con GET una vez arrancado, p. ej. ["/", "/docs", "/usuarios"].
            startup_timeout: Segundos máximos esperando a que el puerto responda.
        """
        paths = paths or ["/"]
        startup_timeout = max(3, min(startup_timeout, 120))
        base = f"http://127.0.0.1:{port}"

        status, _ = _fetch(base + "/", timeout=1)
        if status is not None:
            return f"El puerto {port} ya está en uso por otro proceso. Usa otro puerto."

        with tempfile.TemporaryFile() as log:
            proc = subprocess.Popen(
                ["sh", "-c", command],
                cwd=workdir,
                env=clean_env(),
                stdout=log,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                start_new_session=True,  # grupo propio: se mata el árbol completo
            )
            lines: list[str] = []
            try:
                ready = False
                deadline = time.monotonic() + startup_timeout
                while time.monotonic() < deadline:
                    if proc.poll() is not None:
                        break
                    code, _ = _fetch(base + "/", timeout=1)
                    if code is not None:
                        ready = True
                        break
                    time.sleep(0.5)

                if ready:
                    lines.append(f"Servidor arriba en {base}.")
                    for path in paths:
                        code, body = _fetch(base + (path if path.startswith("/") else "/" + path))
                        lines.append(f"\nGET {path} -> {code}\n{body}")
                elif proc.poll() is not None:
                    lines.append(f"El servidor terminó antes de responder (código {proc.returncode}).")
                else:
                    lines.append(f"El servidor no respondió en {startup_timeout}s.")
            finally:
                try:
                    os.killpg(proc.pid, signal.SIGTERM)
                    proc.wait(timeout=5)
                except ProcessLookupError:
                    pass
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()

            log.seek(0)
            output = log.read().decode("utf-8", "replace")[-3000:]

        lines.append("\nServidor detenido.\n--- log del servidor (final) ---\n" + output)
        return "\n".join(lines)

    return server_check
