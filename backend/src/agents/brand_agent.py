from agno.agent import Agent
from agno.models.anthropic import Claude
from src.prompts.agent_prompts import BRAND_PROMPT

brand_agent = Agent(
    name="Brand Agent",
    model=Claude(id="claude-opus-4-5"),
    tools=[],
    instructions=BRAND_PROMPT,
    markdown=True,
)