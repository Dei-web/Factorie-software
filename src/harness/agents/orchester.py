from pathlib import Path

from strands.vended_tools.handoff_to_user import handoff_to_user
from strands_harness import create_harness

from harness.config.models import model
from harness.prompts.prompt_agent import AGENT_INSTRUCTIONS
from harness.tools.workdir_sandbox import WorkdirSandbox


def create_orchestrator(session_manager, workdir: Path, storage=None):
    return create_harness(
        name="factorie_agent",
        model=model,
        instructions=AGENT_INSTRUCTIONS,
        builtin_tools={
            "*": False,
            "shell": True,
            "read": True,
            "write": True,
            "edit": True,
            "subagent": {"max_depth": 1},
        },
        tools=[handoff_to_user],
        session=session_manager,
        storage=storage,
        sandbox=WorkdirSandbox(workdir),
        # Memoria/skills del harness apagadas: evitan llamadas extra al modelo gratuito
        # y no cargan skills de herramientas que no están instaladas.
        memory=False,
        skills=False,
    )
