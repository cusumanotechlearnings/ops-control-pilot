from agno.agent import Agent
from agno.models.anthropic import Claude
from src.prompts.agent_prompts import ANALYST_PROMPT

analyst_agent = Agent(
    name="Analyst Agent",
    model=Claude(id="claude-opus-4-5"),
    tools=[],
    instructions=ANALYST_PROMPT,
    markdown=True,
)