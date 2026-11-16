# from pathlib import Path

from strands import Agent

# from strands.vended_plugins.skills import AgentSkills
from strands.vended_tools import shell
from strands.vended_tools.handoff_to_user import (
    # HANDOFF_INTERRUPT_NAME,
    handoff_to_user,
)

from harness.config.models import model
from harness.prompts.prompt_spec_writer import SPEC_WRITER_SYSTEM_PROMPT

# BASE_DIR = Path(__file__).resolve().parents[3]
#
# SKILL_PATH = BASE_DIR / ".agents" / "skills" / "agent-browser"
#
# testing_skills = AgentSkills(skills=[str(SKILL_PATH)])


spec_writer_agent = Agent(
    model=model,
    name="spec_writer_agent",
    description="Agente encargado de Gestionar la idea de el usuario.",
    system_prompt=SPEC_WRITER_SYSTEM_PROMPT,
    tools=[handoff_to_user, shell],
)
