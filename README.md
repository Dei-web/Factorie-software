# Factorie-IA

Agente de desarrollo autónomo. Le das una tarea en lenguaje natural y trabaja en un loop (entender, cambiar, verificar) hasta dejarla resuelta: compila, corre los tests, levanta el servidor y revisa la interfaz.

Construido sobre [`strands-harness`](https://pypi.org/project/strands-harness/) con un modelo de NVIDIA.

## Características

- **Un proyecto por conversación:** cada tarea nueva se crea en su propia carpeta dentro de `generated_projects/`.
- **Conversaciones continuas:** el historial se guarda en disco, así que puedes pedir cambios sobre lo ya hecho o reiniciar y seguir donde quedaste.
- **Verificación real:** ejecuta tests, prueba servidores y toma capturas de las interfaces web para revisarlas.
- **CLI y Telegram** como canales de entrada.

## Requisitos

- Python 3.12+ y [`uv`](https://docs.astral.sh/uv/)
- Una API key de [NVIDIA](https://build.nvidia.com/)
- Opcional: Chromium/Chrome headless para las capturas (o define `HARNESS_BROWSER=/ruta/al/navegador`)
- Opcional: un token de bot de Telegram

## Instalación

```bash
git clone git@github.com:Dei-web/Factorie-software.git
cd Factorie-software
uv sync
cp .env.example .env
```

Rellena `.env`:

```env
NVIDIA_API_KEY=...
TELEGRAM_BOT_TOKEN=...   # solo si usas Telegram
```

## Uso

```bash
uv run harness
```

```
Factorie> crea una API REST en FastAPI para gestionar usuarios
Factorie> agrégale autenticación con JWT
```

| Comando              | Descripción                                              |
| -------------------- | -------------------------------------------------------- |
| `/nuevo`             | Empieza una conversación y un proyecto nuevos             |
| `/proyecto <nombre>` | Trabaja sobre un proyecto existente de `generated_projects/` |
| `/proyecto`          | Muestra el proyecto actual                                |
| `exit`               | Sale                                                      |

Para usar Telegram, cambia `run_cli()` por `run_telegram_bot()` en `src/harness/main.py`.

## Estructura

```
src/harness/
├── adapters/inbound/   # CLI y Telegram
├── aplication/         # servicio de tareas y conversaciones
├── agents/             # construcción del agente
├── prompts/            # instrucciones del agente
├── tools/              # sandbox, capturas y prueba de servidores
├── memory/             # persistencia en SQLite
└── config/             # modelo y rutas
```

## Aviso

El agente ejecuta comandos en tu máquina con tus permisos. Úsalo en un entorno de desarrollo y solo con tareas de confianza.
