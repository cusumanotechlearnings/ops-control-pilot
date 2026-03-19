from agno.agent import Agent
from agno.models.anthropic import Claude
from src.prompts.agent_prompts import SEGMENTATION_PROMPT

segmentation_agent = Agent(
    name="Segmentation Agent",
    model=Claude(id="claude-opus-4-5"),
    tools=[],
    instructions=SEGMENTATION_PROMPT,
    markdown=True,
)