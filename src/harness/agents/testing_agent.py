from pathlib import Path

from strands import Agent
from strands.vended_plugins.skills import AgentSkills
from strands.vended_tools import shell

from harness.config.models import model
from harness.mcps.playwright import playwright_client
from harness.prompts.prompt_testing import TESTING_SYSTEM_PROMPT

BASE_DIR = Path(__file__).resolve().parents[3]

SKILL_PATH = BASE_DIR / ".agents" / "skills" / "agent-browser"

testing_skills = AgentSkills(skills=[str(SKILL_PATH)])


testing_agent = Agent(
    model=model,
    name="testing_agent",
    description="Agente encargado de testear las tareas.",
    system_prompt=TESTING_SYSTEM_PROMPT,
    plugins=[testing_skills],
    tools=[playwright_client, shell],
)
