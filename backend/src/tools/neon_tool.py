import os
import re
import psycopg2
import psycopg2.extras
from agno.tools import tool
from dotenv import load_dotenv

load_dotenv()

# Keep tool outputs small so team + session history does not exceed model context.
DEFAULT_QUERY_LIMIT = 50
MAX_ROWS_IN_RESPONSE = 60
MAX_CELL_CHARS = 220
MAX_OUTPUT_CHARS = 12000


def _get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def _apply_safe_default_limit(query: str, normalized: str) -> str:
    """Add a defensive LIMIT when one is missing to control token/cost growth."""
    if re.search(r"\bLIMIT\s+\d+\b", normalized):
        return query
    if not (normalized.startswith("SELECT") or normalized.startswith("WITH")):
        return query
    trimmed = query.strip().rstrip(";")
    return f"{trimmed} LIMIT {DEFAULT_QUERY_LIMIT}"

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
    query = _apply_safe_default_limit(query, normalized)

    try:
        conn = _get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        if not rows:
            return "Query returned no results."

        total_rows = len(rows)
        truncated = total_rows > MAX_ROWS_IN_RESPONSE
        visible = rows[:MAX_ROWS_IN_RESPONSE] if truncated else rows

        def _cell(v) -> str:
            if v is None:
                return ""
            s = str(v)
            if len(s) > MAX_CELL_CHARS:
                return s[: MAX_CELL_CHARS - 3] + "..."
            return s

        headers = list(rows[0].keys())
        header_row = "| " + " | ".join(headers) + " |"
        separator = "| " + " | ".join(["---"] * len(headers)) + " |"
        data_rows = []
        current_chars = len(header_row) + len(separator)
        omitted_due_to_size = 0
        for row in visible:
            rendered = "| " + " | ".join(_cell(v) for v in row.values()) + " |"
            if current_chars + len(rendered) > MAX_OUTPUT_CHARS:
                omitted_due_to_size += 1
                continue
            data_rows.append(rendered)
            current_chars += len(rendered)
        note = ""
        if truncated:
            note = (
                f"\n\n_Showing first {MAX_ROWS_IN_RESPONSE} of {total_rows} rows. "
                "Add LIMIT, tighter filters, or aggregates to reduce size._"
            )
        if omitted_due_to_size:
            note += (
                f"\n\n_Additional {omitted_due_to_size} row(s) omitted to keep output compact. "
                "Request fewer columns or tighter filters for detail._"
            )
        return (
            f"**{total_rows} row(s) returned**"
            + (" (truncated in this view)" if truncated else "")
            + ":\n\n"
            + "\n".join([header_row, separator] + data_rows)
            + note
        )

    except Exception as e:
        return f"SQL Error: {str(e)}\n\nQuery attempted:\n{query}"