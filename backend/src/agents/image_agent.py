from agno.agent import Agent
from agno.models.anthropic import Claude
from src.prompts.agent_prompts import IMAGE_ANALYSIS_PROMPT

image_agent = Agent(
    name="Image Analysis Agent",
    model=Claude(id="claude-opus-4-5"),
    tools=[],
    instructions=IMAGE_ANALYSIS_PROMPT,
    markdown=True,
)