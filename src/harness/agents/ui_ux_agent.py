from strands import Agent

# from strands.vended_plugins.skills import AgentSkills
from strands.vended_tools import shell

from harness.config.models import model
from harness.prompts.prompt_ux_ui import UX_UI_SYSTEM_PROMPT

# ui_ux_skills = AgentSkills(skills=[])

ux_ui_agent = Agent(
    name="coding_agent",
    description="Agente encargado de coordinar la experiencia de usuario",
    system_prompt=UX_UI_SYSTEM_PROMPT,
    # plugins=[ui_ux_skills],
    model=model,
    tools=[shell],
)
