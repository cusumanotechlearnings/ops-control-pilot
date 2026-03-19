import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.team import Team
from agno.models.anthropic import Claude
from agno.db.sqlite import SqliteDb

from src.agents.data_query_agent import data_query_agent
from src.agents.analyst_agent import analyst_agent
from src.agents.creative_agent import creative_agent
from src.agents.segmentation_agent import segmentation_agent
from src.agents.brand_agent import brand_agent
from src.agents.image_agent import image_agent
from src.agents.ops_agent import ops_agent
from src.prompts.agent_prompts import ORCHESTRATOR_PROMPT

load_dotenv()
os.makedirs("data", exist_ok=True)

db = SqliteDb(
    db_file="data/sessions.db",
    session_table="sessions",
)

orchestrator = Team(
    name="Marketing Ops Orchestrator",
    model=Claude(id="claude-opus-4-5"),
    members=[
        data_query_agent,
        analyst_agent,
        creative_agent,
        segmentation_agent,
        brand_agent,
        image_agent,
        ops_agent,
    ],
    instructions=ORCHESTRATOR_PROMPT,
    db=db,
    markdown=True,
    add_history_to_context=True,
    num_history_runs=10,
)

def chat(message: str, session_id: str, user_id: str = "user") -> str:
    response = orchestrator.run(
        message,
        session_id=session_id,
        user_id=user_id
    )
    return response.content