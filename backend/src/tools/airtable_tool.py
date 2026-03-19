import os
from pyairtable import Api
from agno.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool
def create_project_ticket(
    title: str,
    segment: str,
    description: str,
    stakeholders: str
) -> dict:
    """
    Creates a new campaign project in Airtable.
    Only call this after the user has explicitly confirmed they want
    a ticket created. Never call proactively.

    Args:
        title: Project name. Format: "[Segment] [Type] [Term]"
        segment: Target student segment
        description: 2-3 sentence campaign goal summary
        stakeholders: Comma-separated names, default "CMO, VP of Marketing"
    """
    api = Api(os.getenv("AIRTABLE_API_KEY"))
    table = api.table(
        os.getenv("AIRTABLE_BASE_ID"),
        os.getenv("AIRTABLE_PROJECTS_TABLE_ID")
    )
    record = table.create({
        "Title": title,
        "Segment": segment,
        "Description": description,
        "Stakeholders": stakeholders,
        "Status": "Discovery",
    })
    return {
        "success": True,
        "record_id": record["id"],
        "message": f"✅ Project created: **{title}**"
    }

@tool
def create_tasks(project_id: str, tasks: list[str]) -> dict:
    """
    Creates discovery tasks linked to a project in Airtable.
    Always call create_project_ticket first to get the project_id.

    Args:
        project_id: Record ID from create_project_ticket
        tasks: List of task descriptions
    """
    api = Api(os.getenv("AIRTABLE_API_KEY"))
    table = api.table(
        os.getenv("AIRTABLE_BASE_ID"),
        os.getenv("AIRTABLE_TASKS_TABLE_ID")
    )
    created = []
    for task_name in tasks:
        record = table.create({
            "Task": task_name,
            "Project": [project_id],
            "Status": "To Do",
        })
        created.append(record["id"])
    return {
        "success": True,
        "tasks_created": len(created),
        "message": f"✅ Created {len(created)} tasks"
    }