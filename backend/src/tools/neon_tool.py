import os
import psycopg2
import psycopg2.extras
from agno.tools import tool
from dotenv import load_dotenv

load_dotenv()

def _get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

@tool
def execute_sql(query: str) -> str:
    """
    Executes a read-only SQL SELECT query against the marketing ops
    Neon Postgres database. Returns results as a markdown table.

    Only SELECT statements are permitted. Use for any question about
    email performance, journeys, automations, assets, or subscribers.

    Args:
        query: A valid PostgreSQL SELECT statement
    """
    normalized = query.strip().upper()
    forbidden = ['INSERT','UPDATE','DELETE','DROP','CREATE',
                 'ALTER','TRUNCATE','GRANT','REVOKE']
    for word in forbidden:
        if word in normalized:
            return f"Error: '{word}' is not permitted. Only SELECT queries allowed."

    try:
        conn = _get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        if not rows:
            return "Query returned no results."

        headers = list(rows[0].keys())
        header_row = "| " + " | ".join(headers) + " |"
        separator  = "| " + " | ".join(["---"] * len(headers)) + " |"
        data_rows  = [
            "| " + " | ".join(
                str(v) if v is not None else "" for v in row.values()
            ) + " |"
            for row in rows
        ]
        return f"**{len(rows)} rows returned:**\n\n" + \
               "\n".join([header_row, separator] + data_rows)

    except Exception as e:
        return f"SQL Error: {str(e)}\n\nQuery attempted:\n{query}"