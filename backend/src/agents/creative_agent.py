from agno.agent import Agent
from agno.models.anthropic import Claude
from src.prompts.agent_prompts import CREATIVE_PROMPT

creative_agent = Agent(
    name="Creative Agent",
    model=Claude(id="claude-opus-4-5"),
    tools=[],
    instructions=CREATIVE_PROMPT,
    markdown=True,
)