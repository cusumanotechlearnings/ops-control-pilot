import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras

load_dotenv()
os.makedirs("data", exist_ok=True)

from src.agents.orchestrator import chat

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Shared DB helper
# ---------------------------------------------------------------------------

def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise HTTPException(status_code=503, detail="DATABASE_URL not configured")
    return psycopg2.connect(db_url)


def query_db(sql: str, params=None) -> list[dict]:
    conn = get_db_connection()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    user_id: str = "user"

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    response = chat(req.message, req.session_id, req.user_id)
    response_type = (
        "clarification"
        if "?" in response and len(response) < 300
        else "answer"
    )
    return {
        "response": response,
        "response_type": response_type
    }


# ---------------------------------------------------------------------------
# Dashboard — Metrics
# ---------------------------------------------------------------------------

@app.get("/api/metrics/summary")
async def metrics_summary(
    days: int = Query(default=365, ge=7, le=1825),
    date_from: Optional[str] = Query(default=None, description="YYYY-MM-DD"),
    date_to: Optional[str]   = Query(default=None, description="YYYY-MM-DD"),
    business_unit: Optional[str] = Query(default=None),
):
    """
    Aggregate KPI totals. When date_from/date_to are provided they take
    precedence over the relative `days` window. Optionally filter by BU.
    """
    actual_filter = "(is_planned IS FALSE OR is_planned IS NULL)"
    params: dict = {}

    # Date window clause (no aliases — used in the flat dod_metrics table)
    if date_from or date_to:
        parts = []
        if date_from:
            parts.append("send_date >= %(date_from)s")
            params["date_from"] = date_from
        if date_to:
            parts.append("send_date <= %(date_to)s")
            params["date_to"] = date_to
        date_clause = "AND " + " AND ".join(parts)
    else:
        date_clause = (
            f"AND send_date >= "
            f"(SELECT MAX(send_date) FROM dod_metrics WHERE {actual_filter})"
            f" - INTERVAL '{days} days'"
        )

    bu_clause = ""
    if business_unit:
        bu_clause = "AND business_unit = %(business_unit)s"
        params["business_unit"] = business_unit

    # Same clauses but with d. prefix for the sentiment join query
    if date_from or date_to:
        d_parts = []
        if date_from:
            d_parts.append("d.send_date >= %(date_from)s")
        if date_to:
            d_parts.append("d.send_date <= %(date_to)s")
        d_date_clause = "AND " + " AND ".join(d_parts)
    else:
        d_date_clause = (
            f"AND d.send_date >= "
            f"(SELECT MAX(send_date) FROM dod_metrics WHERE {actual_filter})"
            f" - INTERVAL '{days} days'"
        )
    d_bu_clause = "AND d.business_unit = %(business_unit)s" if business_unit else ""

    sql = f"""
        SELECT
            business_unit,
            SUM(total_sends)        AS total_sends,
            SUM(deliveries)         AS deliveries,
            SUM(total_opens)        AS total_opens,
            SUM(total_clicks)       AS total_clicks,
            AVG(open_rate)          AS avg_open_rate,
            AVG(click_rate)         AS avg_click_rate,
            AVG(delivery_rate)      AS avg_delivery_rate,
            AVG(click_to_open_rate) AS avg_ctor
        FROM dod_metrics
        WHERE {actual_filter}
          {date_clause}
          {bu_clause}
        GROUP BY business_unit
        ORDER BY business_unit
    """
    overall_sql = f"""
        SELECT
            SUM(total_sends)        AS total_sends,
            SUM(deliveries)         AS deliveries,
            SUM(total_opens)        AS total_opens,
            SUM(total_clicks)       AS total_clicks,
            AVG(open_rate)          AS avg_open_rate,
            AVG(click_rate)         AS avg_click_rate,
            AVG(delivery_rate)      AS avg_delivery_rate,
            AVG(click_to_open_rate) AS avg_ctor,
            MAX(send_date)          AS latest_date,
            MIN(send_date)          AS earliest_date
        FROM dod_metrics
        WHERE {actual_filter}
          {date_clause}
          {bu_clause}
    """
    sentiment_sql = f"""
        SELECT AVG(v.sentiment_value) AS avg_sentiment
        FROM voc_responses v
        JOIN dod_metrics d ON v.dod_metric_id = d.id
        WHERE (d.is_planned IS FALSE OR d.is_planned IS NULL)
          {d_date_clause}
          {d_bu_clause}
    """

    try:
        rows = query_db(sql, params or None)
        overall = query_db(overall_sql, params or None)
        result = overall[0] if overall else {}
        for col in ("latest_date", "earliest_date"):
            if result.get(col):
                result[col] = str(result[col])
        sentiment = query_db(sentiment_sql, params or None)
        result["avg_sentiment"] = float(sentiment[0]["avg_sentiment"]) if sentiment and sentiment[0].get("avg_sentiment") is not None else None
        return {"by_bu": rows, "overall": result, "days": days}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics/trend")
async def metrics_trend(
    days: int = Query(default=90, ge=7, le=730),
    date_from: Optional[str] = Query(default=None, description="YYYY-MM-DD"),
    date_to: Optional[str]   = Query(default=None, description="YYYY-MM-DD"),
    business_unit: Optional[str] = Query(default=None),
):
    """
    Daily delivery/open/click/sentiment counts broken down by business_unit.
    When date_from/date_to are provided they override the relative `days` window.
    """
    actual_filter = "(d.is_planned IS FALSE OR d.is_planned IS NULL)"
    anchor_filter = "(is_planned IS FALSE OR is_planned IS NULL)"
    params: dict = {}

    if date_from or date_to:
        d_parts = []
        if date_from:
            d_parts.append("d.send_date >= %(date_from)s")
            params["date_from"] = date_from
        if date_to:
            d_parts.append("d.send_date <= %(date_to)s")
            params["date_to"] = date_to
        date_clause = "AND " + " AND ".join(d_parts)
    else:
        date_clause = (
            f"AND d.send_date >= "
            f"(SELECT MAX(send_date) FROM dod_metrics WHERE {anchor_filter})"
            f" - INTERVAL '{days} days'"
        )

    bu_clause = ""
    if business_unit:
        bu_clause = "AND d.business_unit = %(business_unit)s"
        params["business_unit"] = business_unit

    sql = f"""
        SELECT
            d.send_date,
            d.business_unit,
            SUM(d.total_sends)         AS total_sends,
            SUM(d.deliveries)          AS deliveries,
            SUM(d.total_opens)         AS total_opens,
            SUM(d.total_clicks)        AS total_clicks,
            AVG(d.open_rate)           AS avg_open_rate,
            AVG(d.click_rate)          AS avg_click_rate,
            AVG(v.sentiment_value)     AS avg_sentiment
        FROM dod_metrics d
        LEFT JOIN voc_responses v ON v.dod_metric_id = d.id
        WHERE {actual_filter}
          {date_clause}
          {bu_clause}
        GROUP BY d.send_date, d.business_unit
        ORDER BY d.send_date ASC, d.business_unit
    """
    try:
        rows = query_db(sql, params or None)
        for row in rows:
            if row.get("send_date"):
                row["send_date"] = str(row["send_date"])
            if row.get("avg_sentiment") is not None:
                row["avg_sentiment"] = float(row["avg_sentiment"])
        return {"trend": rows}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Dashboard — Journeys
# ---------------------------------------------------------------------------

@app.get("/api/journeys")
async def journeys_list(
    status: Optional[str] = Query(default=None),
    business_unit: Optional[str] = Query(default=None),
):
    """
    List journeys with their latest send date and entry source frequency.
    Optionally filter by status (Active, Stopped, Draft, Paused, Complete)
    and/or business_unit.
    """
    params: dict = {}
    status_filter = ""
    if status:
        status_filter = "AND j.status = %(status)s"
        params["status"] = status
    bu_filter = ""
    if business_unit:
        bu_filter = "AND j.business_unit = %(business_unit)s"
        params["business_unit"] = business_unit

    sql = f"""
        SELECT
            j.journey_id,
            j.journey_name,
            j.business_unit,
            j.status,
            j.target_audience,
            j.department,
            j.created_date,
            j.last_modified_date,
            MAX(d.send_date)            AS last_send_date,
            MIN(d.send_date)            AS first_send_date,
            jes.schedule_frequency,
            jes.schedule_start_time,
            jes.schedule_end_time
        FROM journeys j
        LEFT JOIN dod_metrics d      ON d.journey_id = j.journey_id
        LEFT JOIN journey_entry_sources jes ON jes.journey_id = j.journey_id
        WHERE 1=1
        {status_filter}
        {bu_filter}
        GROUP BY
            j.journey_id, j.journey_name, j.business_unit, j.status,
            j.target_audience, j.department, j.created_date, j.last_modified_date,
            jes.schedule_frequency, jes.schedule_start_time, jes.schedule_end_time
        ORDER BY j.status, j.journey_name
    """
    try:
        rows = query_db(sql, params or None)
        for row in rows:
            for date_col in ("last_send_date", "first_send_date", "created_date",
                             "last_modified_date", "schedule_start_time", "schedule_end_time"):
                if row.get(date_col):
                    row[date_col] = str(row[date_col])
        return {"journeys": rows}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Dashboard — Sends Calendar
# ---------------------------------------------------------------------------

@app.get("/api/sends/calendar")
async def sends_calendar(
    year: int = Query(default=None),
    month: int = Query(default=None, ge=1, le=12),
):
    """
    Count of email sends per calendar day for the given month/year.
    Defaults to the month of the latest send_date in the database so the
    calendar always opens on a month that has actual data.
    """
    if year is None or month is None:
        latest = query_db("SELECT MAX(send_date) AS d FROM dod_metrics")
        if latest and latest[0].get("d"):
            anchor = latest[0]["d"]
            y = year if year is not None else anchor.year
            m = month if month is not None else anchor.month
        else:
            from datetime import date
            today = date.today()
            y = year if year is not None else today.year
            m = month if month is not None else today.month
    else:
        y = year
        m = month

    sql = """
        SELECT
            send_date,
            COUNT(DISTINCT job_id)                              AS send_count,
            SUM(total_sends)                                    AS total_sends,
            SUM(CASE WHEN is_planned IS FALSE OR is_planned IS NULL
                     THEN deliveries ELSE 0 END)                AS deliveries,
            AVG(CASE WHEN is_planned IS FALSE OR is_planned IS NULL
                     THEN open_rate  END)                       AS avg_open_rate,
            AVG(CASE WHEN is_planned IS FALSE OR is_planned IS NULL
                     THEN click_rate END)                       AS avg_click_rate,
            BOOL_OR(is_planned = TRUE)                          AS has_planned,
            BOOL_OR(is_planned IS FALSE OR is_planned IS NULL)  AS has_actual,
            array_agg(DISTINCT email_name   ORDER BY email_name) AS email_names,
            array_agg(DISTINCT journey_name ORDER BY journey_name)
                FILTER (WHERE journey_name IS NOT NULL)         AS journey_names
        FROM dod_metrics
        WHERE EXTRACT(YEAR  FROM send_date) = %(year)s
          AND EXTRACT(MONTH FROM send_date) = %(month)s
        GROUP BY send_date
        ORDER BY send_date
    """
    try:
        rows = query_db(sql, {"year": y, "month": m})
        for row in rows:
            if row.get("send_date"):
                row["send_date"] = str(row["send_date"])
        return {"year": y, "month": m, "days": rows}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Dashboard — Upcoming Sends Calendar (future planned sends)
# ---------------------------------------------------------------------------

@app.get("/api/sends/upcoming-calendar")
async def upcoming_sends_calendar(
    year: int = Query(default=None),
    month: int = Query(default=None, ge=1, le=12),
    business_unit: Optional[str] = Query(default=None),
):
    """
    Upcoming journey calendar for the given month/year, optionally filtered
    by business_unit. Defaults to the current calendar month.
    """
    from datetime import date as _date
    today = _date.today()
    y = year if year is not None else today.year
    m = month if month is not None else today.month

    params: dict = {"year": y, "month": m}
    bu_filter = ""
    if business_unit:
        bu_filter = "AND j.business_unit = %(business_unit)s"
        params["business_unit"] = business_unit

    sql = f"""
        SELECT
            DATE(jes.schedule_start_time)                               AS send_date,
            COUNT(*)                                                    AS send_count,
            0                                                           AS total_sends,
            0                                                           AS deliveries,
            NULL::NUMERIC                                               AS avg_open_rate,
            NULL::NUMERIC                                               AS avg_click_rate,
            TRUE                                                        AS has_planned,
            FALSE                                                       AS has_actual,
            ARRAY[]::TEXT[]                                             AS email_names,
            array_agg(j.journey_name ORDER BY j.journey_name)          AS journey_names
        FROM journey_entry_sources jes
        JOIN journeys j ON j.journey_id = jes.journey_id
        WHERE EXTRACT(YEAR  FROM jes.schedule_start_time) = %(year)s
          AND EXTRACT(MONTH FROM jes.schedule_start_time) = %(month)s
          {bu_filter}
        GROUP BY DATE(jes.schedule_start_time)
        ORDER BY DATE(jes.schedule_start_time)
    """
    try:
        rows = query_db(sql, params)
        for row in rows:
            if row.get("send_date"):
                row["send_date"] = str(row["send_date"])
        return {"year": y, "month": m, "days": rows}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Dashboard — Email / Asset Search
# ---------------------------------------------------------------------------

@app.get("/api/search/emails")
async def search_emails(
    copy: Optional[str]         = Query(default=None, description="Search subject, pre-header, or name"),
    business_unit: Optional[str] = Query(default=None),
    date_from: Optional[str]    = Query(default=None, description="YYYY-MM-DD"),
    date_to: Optional[str]      = Query(default=None, description="YYYY-MM-DD"),
    sender: Optional[str]       = Query(default=None),
    limit: int                  = Query(default=100, ge=1, le=500),
):
    """
    Deterministic email search against email_assets joined to dod_metrics
    for the most recent send performance of each asset.
    """
    conditions = []
    params: dict = {"limit": limit}

    if copy:
        conditions.append(
            "(ea.name ILIKE %(copy)s OR ea.subject_line ILIKE %(copy)s OR ea.pre_header ILIKE %(copy)s)"
        )
        params["copy"] = f"%{copy}%"
    if business_unit:
        conditions.append("ea.business_unit = %(business_unit)s")
        params["business_unit"] = business_unit
    if sender:
        conditions.append("ea.sender_address ILIKE %(sender)s")
        params["sender"] = f"%{sender}%"

    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    date_filter = ""
    if date_from:
        date_filter += " AND d.send_date >= %(date_from)s"
        params["date_from"] = date_from
    if date_to:
        date_filter += " AND d.send_date <= %(date_to)s"
        params["date_to"] = date_to

    sql = f"""
        SELECT
            ea.asset_id,
            ea.business_unit,
            ea.name                     AS email_name,
            ea.subject_line,
            ea.pre_header,
            ea.sender_address,
            ea.folder,
            ea.department_code,
            ea.created_time,
            ea.last_modified_date,
            agg.total_sends,
            agg.deliveries,
            agg.avg_open_rate,
            agg.avg_click_rate,
            agg.last_send_date,
            agg.send_count
        FROM email_assets ea
        LEFT JOIN (
            SELECT
                email_asset_id,
                SUM(total_sends)   AS total_sends,
                SUM(deliveries)    AS deliveries,
                AVG(open_rate)     AS avg_open_rate,
                AVG(click_rate)    AS avg_click_rate,
                MAX(send_date)     AS last_send_date,
                COUNT(*)           AS send_count
            FROM dod_metrics d
            WHERE 1=1 {date_filter}
            GROUP BY email_asset_id
        ) agg ON agg.email_asset_id = ea.asset_id
        {where_clause}
        ORDER BY agg.last_send_date DESC NULLS LAST, ea.name
        LIMIT %(limit)s
    """
    try:
        rows = query_db(sql, params)
        for row in rows:
            for col in ("created_time", "last_modified_date", "last_send_date"):
                if row.get(col):
                    row[col] = str(row[col])
        return {"results": rows, "count": len(rows)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok"}