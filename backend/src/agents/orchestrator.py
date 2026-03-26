import os
import json
import re
from typing import TypedDict
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
    num_history_messages=8,
    max_tool_calls_from_history=0,
    enable_session_summaries=False,
    add_session_summary_to_context=False,
    compress_tool_results=True,
    max_iterations=3,
    tool_call_limit=2,
)

IMAGE_PAYLOAD_PATTERN = re.compile(
    r"<image_payload>\s*(\{.*?\})\s*</image_payload>",
    flags=re.DOTALL,
)
ALLOWED_IMAGE_MIME_TYPES = {"image/png", "image/jpeg", "image/webp"}
MAX_IMAGE_BASE64_CHARS = 8_000_000


class ChatResult(TypedDict):
    response: str
    image_base64: str | None
    image_mime_type: str | None
    image_alt: str | None


def _extract_image_payload(content: str) -> ChatResult:
    image_base64 = None
    image_mime_type = None
    image_alt = None

    match = IMAGE_PAYLOAD_PATTERN.search(content or "")
    cleaned_content = IMAGE_PAYLOAD_PATTERN.sub("", content or "").strip()

    if match:
        try:
            payload = json.loads(match.group(1))
            raw_b64 = payload.get("image_base64")
            raw_mime = payload.get("image_mime_type")
            raw_alt = payload.get("image_alt")

            if (
                isinstance(raw_b64, str)
                and isinstance(raw_mime, str)
                and raw_mime in ALLOWED_IMAGE_MIME_TYPES
                and len(raw_b64) <= MAX_IMAGE_BASE64_CHARS
            ):
                image_base64 = raw_b64
                image_mime_type = raw_mime
                image_alt = raw_alt if isinstance(raw_alt, str) else "Generated image"
        except json.JSONDecodeError:
            pass

    return {
        "response": cleaned_content,
        "image_base64": image_base64,
        "image_mime_type": image_mime_type,
        "image_alt": image_alt,
    }


def chat(message: str, session_id: str, user_id: str = "user") -> ChatResult:
    response = orchestrator.run(
        message,
        session_id=session_id,
        user_id=user_id
    )
    content = response.content if isinstance(response.content, str) else str(response.content)
    return _extract_image_payload(content)