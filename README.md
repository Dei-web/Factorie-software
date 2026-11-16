# Factorie-IA

**Agente de desarrollo autónomo:** le das una tarea en lenguaje natural ("crea una API con arquitectura hexagonal", "la calculadora está fallando") y trabaja en un loop — entender → cambiar → verificar → repetir — hasta dejarla resuelta y **verificada de verdad**: compila, corre los tests, levanta el servidor, mira la interfaz.

Hoy corre sobre [`strands-harness`](https://pypi.org/project/strands-harness/) con un modelo gratuito (NVIDIA Nemotron). La meta es que sea **independiente del harness y del modelo**: poder enchufar Claude, Codex o un harness propio sin cambiar cómo se usa.

> Estado: en desarrollo activo, uso personal. Funciona para tareas pequeñas y medianas (bugs, CRUDs, APIs, webs). Las tareas largas y complejas todavía son experimentales.

---

## Cómo funciona

```
 CLI / Telegram ──► SubmitTask ──► Agente (strands-harness) ──► generated_projects/<proyecto>/
   (adaptadores)    (conversación      │
                     persistente)      ├─ shell · read · write · edit
                                       ├─ todo_write (plan de pasos)
                                       ├─ screenshot   → ve la interfaz renderizada
                                       ├─ server_check → arranca, prueba y apaga servidores
                                       ├─ subagent     → subtareas en contexto limpio
                                       └─ handoff_to_user → pregunta solo si está bloqueado
```

- **Un proyecto por conversación.** Cada tarea nueva crea su carpeta en `generated_projects/` (p. ej. `api-fastapi-db-has-a3fd/`). Con `/proyecto <nombre>` retomas uno existente.
- **Conversaciones continuas.** El historial se guarda en disco (SQLite + sesiones de Strands): puedes decir "ahora agrégale autenticación" o reiniciar el proceso y seguir donde quedaste.
- **Verificación real, no "parece que funciona".**
  - Código → compila y ejecuta los tests.
  - Servidores → `server_check` lo arranca, hace peticiones y **siempre** lo detiene (sin procesos colgados).
  - Interfaces web → `screenshot` renderiza la página en Chromium headless y le pasa la imagen al modelo (con visión) para que critique y corrija.
- **Entornos separados.** Los comandos del agente corren dentro del proyecto generado y sin heredar el entorno virtual del harness.

## Requisitos

- Python 3.12+ y [`uv`](https://docs.astral.sh/uv/)
- Una API key de [NVIDIA](https://build.nvidia.com/) (gratuita)
- Opcional, para `screenshot`: un Chromium/Chrome headless. Si tienes Playwright instalado se usa el de `~/.cache/ms-playwright`; si no, define `HARNESS_BROWSER=/ruta/al/navegador`.
- Opcional: un bot de Telegram (token de [@BotFather](https://t.me/BotFather))

## Instalación

```bash
git clone git@github.com:Dei-web/Factorie-software.git
cd Factorie-software
uv sync
cp .env.example .env   # y rellena las claves
```

`.env`:

```env
NVIDIA_API_KEY=nvapi-...
TELEGRAM_BOT_TOKEN=...   # solo si usas Telegram
```

## Uso

### CLI

```bash
uv run harness
```

```
Factorie> crea una API REST en FastAPI con arquitectura hexagonal para gestionar usuarios
Factorie> agrégale autenticación con JWT
Factorie> /nuevo
Factorie> /proyecto api-fastapi-db-has-a3fd
Factorie> verifica que el servidor levanta y que los tests pasan
```

| Comando              | Qué hace                                                        |
| -------------------- | --------------------------------------------------------------- |
| `/nuevo`             | Empieza una conversación nueva (y una carpeta de proyecto nueva) |
| `/proyecto <nombre>` | La siguiente tarea trabaja sobre `generated_projects/<nombre>`   |
| `/proyecto`          | Muestra el proyecto actual                                       |
| `exit`               | Sale                                                             |

Si el agente necesita una decisión que solo tú puedes tomar, se detiene y te pregunta; tu respuesta continúa la misma ejecución.

### Telegram

En `src/harness/main.py` cambia `run_cli()` por `run_telegram_bot()` y ejecuta `uv run harness`. Cada chat tiene su propia conversación y admite `/nuevo` y `/proyecto <nombre>`.

## Estructura

Arquitectura hexagonal: los canales de entrada y el motor del agente son intercambiables.

```
src/harness/
├── main.py                       # punto de entrada
├── factorie.py                   # ensambla agente + sesión + proyecto por conversación
├── adapters/inbound/             # canales de entrada: cli.py, telegram.py
├── aplication/
│   ├── port/task_input.py        # contrato de entrada (submit / reset)
│   └── services/submit_task.py   # conversaciones, interrupciones y continuidad
├── agents/orchester.py           # construcción del agente (create_harness)
├── prompts/prompt_agent.py       # instrucciones del agente
├── tools/
│   ├── workdir_sandbox.py        # ejecuta en el proyecto, con entorno limpio
│   ├── screenshot.py             # captura de páginas para verificación visual
│   └── server_check.py           # prueba de servidores con apagado garantizado
├── memory/                       # SQLite: ejecuciones y conversaciones
└── config/                       # modelo y rutas
data/                             # (ignorado) base de datos y sesiones
generated_projects/               # (ignorado) proyectos creados por el agente
```

## Configuración

| Qué                      | Dónde                         |
| ------------------------ | ----------------------------- |
| Modelo, temperatura      | `src/harness/config/models.py` |
| Herramientas del agente  | `src/harness/agents/orchester.py` |
| Comportamiento / reglas  | `src/harness/prompts/prompt_agent.py` |
| Navegador para capturas  | variable `HARNESS_BROWSER`    |

## ⚠️ Seguridad

El agente ejecuta comandos **directamente en tu máquina, con tus permisos** (el sandbox actual fija el directorio y limpia el entorno, pero **no aísla**). Úsalo solo con tareas tuyas y en una máquina de desarrollo. Antes de exponerlo a entradas de terceros (issues públicos, otros usuarios de Telegram) hay que correrlo en un contenedor — ver roadmap.

## Roadmap

**Motor intercambiable**
- [ ] Puerto `AgentEngine` para desacoplar el núcleo de `strands-harness`
- [ ] Adaptador **Claude** (Claude Agent SDK / Claude Code)
- [ ] Adaptador **Codex**
- [ ] **Harness propio**: loop, herramientas y gestión de contexto hechos a medida
- [ ] Router de modelos: gratuito para el grueso, uno más fuerte para planificar o desatascar

**Tareas más grandes**
- [ ] Flujo SDD: issue → `specs/<n>.md` con criterios de aceptación → tests → implementación
- [ ] Plan por hitos persistente (`PLAN.md`) con verificación en cada hito
- [ ] Skills de diseño (sistema visual, componentes) para frontends de calidad

**Integraciones y seguridad**
- [ ] Sandbox en Docker
- [ ] Adaptador de GitHub: atender issues etiquetados y abrir PRs (nunca push directo)
- [ ] Guard de herramientas: reglas deterministas + política para comandos riesgosos
- [ ] Suite de evaluación: escalera de tareas para medir cada cambio del harness
