from strands import Agent
from strands.vended_plugins.skills import AgentSkills
from strands.vended_tools import shell

from harness.config.models import model
from harness.prompts.promp_coding import CODING_SYSTEM_PROMPT

# coding_skills = AgentSkills(skills=[])


coding_agent = Agent(
    name="coding_agent",
    model=model,
    description="Agente encargado de codificar las tareas",
    system_prompt=CODING_SYSTEM_PROMPT,
    tools=[shell],
    # plugins=[coding_skills],
)
