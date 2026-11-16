import glob
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from strands import tool

# Prioridad: variable de entorno > navegador del sistema > Chromium headless de Playwright en caché.
_SYSTEM_BROWSERS = ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable")
_PLAYWRIGHT_GLOB = "~/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell*/chrome-headless-shell"


def find_browser() -> str | None:
    if os.environ.get("HARNESS_BROWSER"):
        return os.environ["HARNESS_BROWSER"]
    for name in _SYSTEM_BROWSERS:
        if path := shutil.which(name):
            return path
    candidates = sorted(glob.glob(os.path.expanduser(_PLAYWRIGHT_GLOB)))
    return candidates[-1] if candidates else None


def make_screenshot_tool(workdir: Path):
    workdir = Path(workdir).resolve()

    @tool
    def screenshot(target: str, width: int = 1280, height: int = 2000) -> dict:
        """Renderiza una página web en un navegador real y te devuelve la imagen para que la MIRES.

        Úsala para verificar cualquier interfaz web: después de crearla y después de cada cambio
        visual. Revisa críticamente la imagen: ¿se ve todo el contenido importante?, ¿la tipografía
        y el estilo son los pedidos?, ¿hay elementos rotos, solapados o vacíos?

        Args:
            target: Ruta a un .html del proyecto (relativa al proyecto) o una URL http(s)://.
            width: Ancho del viewport en px. Usa 390 para revisar la versión móvil.
            height: Alto capturado en px (la captura no hace scroll; aumenta si la página es larga).
        """
        browser = find_browser()
        if browser is None:
            return {
                "status": "error",
                "content": [{"text": "No hay navegador headless disponible (define HARNESS_BROWSER)."}],
            }

        if target.startswith(("http://", "https://", "file://")):
            url = target
        else:
            path = Path(target)
            path = path if path.is_absolute() else workdir / path
            if not path.exists():
                return {"status": "error", "content": [{"text": f"No existe el archivo: {path}"}]}
            url = path.resolve().as_uri()

        height = max(300, min(height, 6000))
        width = max(320, min(width, 1920))

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "shot.png"
            proc = subprocess.run(
                [
                    browser,
                    "--headless",
                    "--disable-gpu",
                    "--hide-scrollbars",
                    "--no-first-run",
                    "--enable-logging=stderr",
                    "--v=0",
                    f"--window-size={width},{height}",
                    "--virtual-time-budget=4000",
                    f"--screenshot={out}",
                    url,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if not out.exists():
                return {
                    "status": "error",
                    "content": [{"text": f"No se pudo capturar {url}:\n{proc.stderr[-1500:]}"}],
                }
            image = out.read_bytes()

        console = [
            line.split("] ", 1)[-1]
            for line in proc.stderr.splitlines()
            if "CONSOLE" in line or "Uncaught" in line
        ]
        report = f"Captura de {url} a {width}x{height}px."
        report += (
            "\nErrores/mensajes de consola:\n" + "\n".join(console[:20])
            if console
            else "\nSin mensajes de consola."
        )

        return {
            "status": "success",
            "content": [
                {"text": report},
                {"image": {"format": "png", "source": {"bytes": image}}},
            ],
        }

    return screenshot
