from agno.agent import Agent
from agno.models.anthropic import Claude
from src.tools.neon_tool import execute_sql
from src.prompts.agent_prompts import DATA_QUERY_PROMPT

data_query_agent = Agent(
    name="Data Query Agent",
    model=Claude(id="claude-opus-4-5"),
    tools=[execute_sql],
    instructions=DATA_QUERY_PROMPT,
    markdown=True,
)