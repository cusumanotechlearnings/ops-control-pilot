from agno.agent import Agent
from agno.models.anthropic import Claude
from src.tools.airtable_tool import create_project_ticket, create_tasks
from src.prompts.agent_prompts import OPS_PM_PROMPT

ops_agent = Agent(
    name="Ops PM Agent",
    model=Claude(id="claude-opus-4-5"),
    tools=[create_project_ticket, create_tasks],
    instructions=OPS_PM_PROMPT,
    markdown=True,
)