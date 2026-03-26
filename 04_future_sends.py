"""
04_future_sends.py — Avalon University Marketing Ops AI
Projects future planned sends into dod_metrics from tomorrow through
August 31, 2026 for all Active journeys.

  • Adds is_planned BOOLEAN column to dod_metrics (safe to re-run)
  • Uses historical avg metrics per journey as the projected baseline
  • Respects schedule_frequency (Daily / Weekly / Monthly / Once)
  • Calendar shows planned + actual; KPI metrics filter to actual only

Run:
  python 04_future_sends.py
"""

import os, random, uuid
from datetime import date, timedelta
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

FUTURE_END = date(2026, 8, 31)
TODAY      = date.today()

random.seed(99)


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def add_column(conn):
    """Add is_planned column if it doesn't exist."""
    cur = conn.cursor()
    cur.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'dod_metrics' AND column_name = 'is_planned'
            ) THEN
                ALTER TABLE dod_metrics ADD COLUMN is_planned BOOLEAN DEFAULT FALSE;
            END IF;
        END
        $$;
    """)
    conn.commit()
    cur.close()
    print("✓  is_planned column ready")


def load_active_journeys(conn):
    """
    Return active journeys joined to their activities and entry source schedule.
    """
    sql = """
        SELECT
            j.journey_id,
            j.journey_name,
            j.business_unit,
            j.status,
            j.target_audience,
            j.department,
            ja.activity_id,
            ja.email_id        AS email_asset_id,
            ja.email_name,
            ja.email_subject   AS subject_line,
            ja.target_audience AS activity_audience,
            COALESCE(jes.schedule_frequency, 'Weekly') AS schedule_frequency
        FROM journeys j
        JOIN journey_activities ja ON ja.journey_id = j.journey_id
        LEFT JOIN journey_entry_sources jes ON jes.journey_id = j.journey_id
        WHERE j.status = 'Active'
          AND ja.activity_type = 'EMAIL'
          AND ja.email_id IS NOT NULL
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    return [dict(r) for r in rows]


def load_historical_baselines(conn):
    """Return avg metrics per journey_id from past actual sends."""
    sql = """
        SELECT
            journey_id,
            AVG(open_rate)          AS avg_open_rate,
            AVG(click_rate)         AS avg_click_rate,
            AVG(delivery_rate)      AS avg_delivery_rate,
            AVG(click_to_open_rate) AS avg_ctor,
            AVG(bounce_rate)        AS avg_bounce_rate,
            AVG(total_sends)        AS avg_sends,
            AVG(open_rate)          AS base_or
        FROM dod_metrics
        WHERE (is_planned IS FALSE OR is_planned IS NULL)
          AND journey_id IS NOT NULL
        GROUP BY journey_id
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    return {r["journey_id"]: dict(r) for r in rows}


def global_baseline(conn):
    """Fallback averages when a journey has no history."""
    sql = """
        SELECT
            AVG(open_rate)          AS avg_open_rate,
            AVG(click_rate)         AS avg_click_rate,
            AVG(delivery_rate)      AS avg_delivery_rate,
            AVG(click_to_open_rate) AS avg_ctor,
            AVG(bounce_rate)        AS avg_bounce_rate,
            AVG(total_sends)        AS avg_sends
        FROM dod_metrics
        WHERE is_planned IS FALSE OR is_planned IS NULL
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql)
    row = cur.fetchone()
    cur.close()
    return dict(row) if row else {
        "avg_open_rate": 0.30, "avg_click_rate": 0.05,
        "avg_delivery_rate": 0.97, "avg_ctor": 0.15,
        "avg_bounce_rate": 0.03, "avg_sends": 800,
    }


def send_dates(start: date, end: date, frequency: str):
    """Yield send dates from start to end based on frequency."""
    interval = {
        "Daily":   1,
        "Weekly":  7,
        "Monthly": 30,
        "Once":    None,
    }.get(frequency, 7)

    if interval is None:
        yield start
        return

    d = start
    while d <= end:
        yield d
        d += timedelta(days=interval)


def rand_rate(base, spread=0.03):
    return round(max(0.001, min(0.999, base + random.gauss(0, spread))), 6)


def build_rows(journeys, baselines, fallback, existing_keys):
    rows = []
    start = TODAY + timedelta(days=1)

    for j in journeys:
        jid      = j["journey_id"]
        jname    = j["journey_name"]
        bu       = j["business_unit"]
        email_id = j["email_asset_id"]
        email_nm = j["email_name"] or ""
        subject  = j["subject_line"] or ""
        audience = j["activity_audience"] or j["target_audience"] or ""
        dept     = j["department"] or ""
        freq     = j["schedule_frequency"]

        b = baselines.get(jid, fallback)
        base_or   = float(b.get("avg_open_rate")   or fallback["avg_open_rate"])
        base_ctr  = float(b.get("avg_click_rate")  or fallback["avg_click_rate"])
        base_dr   = float(b.get("avg_delivery_rate") or fallback["avg_delivery_rate"])
        base_ctor = float(b.get("avg_ctor")        or fallback["avg_ctor"])
        base_br   = float(b.get("avg_bounce_rate") or fallback["avg_bounce_rate"])
        base_snds = int(float(b.get("avg_sends")   or fallback["avg_sends"]))

        for sd in send_dates(start, FUTURE_END, freq):
            key = (email_id or email_nm, str(sd))
            if key in existing_keys:
                continue

            sends   = max(10, int(base_snds * random.uniform(0.85, 1.15)))
            deliv   = int(sends * rand_rate(base_dr, 0.01))
            bounces = sends - deliv
            u_opens = int(deliv * rand_rate(base_or, 0.03))
            opens   = int(u_opens / random.uniform(0.70, 0.85))
            u_clk   = int(u_opens * rand_rate(base_ctr * 2, 0.02))
            clicks  = int(u_clk / random.uniform(0.65, 0.80))
            unsubs  = max(0, int(sends * rand_rate(0.002, 0.001)))

            or_c  = round(u_opens / deliv,  6) if deliv > 0 else 0
            ctr_c = round(u_clk   / deliv,  6) if deliv > 0 else 0
            dr_c  = round(deliv   / sends,  6) if sends > 0 else 0
            ctor  = round(u_clk   / u_opens,6) if u_opens > 0 else 0
            br_c  = round(bounces / sends,  6) if sends > 0 else 0

            job_id = str(random.randint(4000000, 4999999))

            rows.append((
                job_id,
                f"{email_nm}{sd.strftime('%b %d %Y')}",
                f"{email_nm}_{job_id}_{sd.strftime('%Y%m%d')}",
                bu, email_nm, email_id,
                jname, jid,
                "Active", 1,
                f"{jid}_1",
                f"{dept.lower()}@avalon.edu" if dept else "noreply@avalon.edu",
                f"Avalon {dept}" if dept else "Avalon University",
                subject,
                sd, sends, deliv, bounces,
                opens, u_opens, clicks, u_clk, unsubs,
                or_c, ctr_c, dr_c, ctor, br_c,
                audience, dept, audience,
                True,  # is_planned
            ))
            existing_keys.add(key)

    return rows


def load_existing_keys(conn):
    cur = conn.cursor()
    cur.execute("SELECT email_asset_id, send_date FROM dod_metrics WHERE send_date > %s", (TODAY,))
    keys = {(r[0], str(r[1])) for r in cur.fetchall()}
    cur.close()
    return keys


def insert_rows(conn, rows):
    if not rows:
        print("  No new rows to insert.")
        return 0

    sql = """
        INSERT INTO dod_metrics
            (job_id, id_combo, unique_email_send,
             business_unit, email_name, email_asset_id,
             journey_name, journey_id, journey_status,
             journey_version, unique_journey_id_version,
             sender_address, sender_name, subject_line, send_date,
             total_sends, deliveries, total_bounces,
             total_opens, unique_opens, total_clicks, unique_clicks,
             total_unsubscribes,
             open_rate, click_rate, delivery_rate,
             click_to_open_rate, bounce_rate,
             target_segment, department_code, target_audience,
             is_planned)
        VALUES %s
        ON CONFLICT DO NOTHING
    """
    cur = conn.cursor()
    batch_size = 2000
    inserted = 0
    for i in range(0, len(rows), batch_size):
        psycopg2.extras.execute_values(cur, sql, rows[i:i+batch_size])
        conn.commit()
        inserted += cur.rowcount
    cur.close()
    return inserted


def main():
    if not DATABASE_URL:
        print("❌  DATABASE_URL not set in .env"); raise SystemExit(1)

    conn = get_conn()

    print("Step 1/5  Adding is_planned column...")
    add_column(conn)

    print("Step 2/5  Loading active journeys and activities...")
    journeys = load_active_journeys(conn)
    print(f"          {len(journeys)} active email activities found")

    if not journeys:
        print("          No active journeys found — make sure 02_seed_data.py was run first.")
        conn.close(); return

    print("Step 3/5  Loading historical baselines...")
    baselines = load_historical_baselines(conn)
    fallback  = global_baseline(conn)

    print("Step 4/5  Generating future send rows...")
    existing_keys = load_existing_keys(conn)
    rows = build_rows(journeys, baselines, fallback, existing_keys)
    print(f"          {len(rows):,} planned send rows generated "
          f"({(TODAY + timedelta(days=1)).isoformat()} → {FUTURE_END.isoformat()})")

    print("Step 5/5  Inserting rows...")
    n = insert_rows(conn, rows)
    print(f"          {n:,} rows inserted")

    # Summary
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM dod_metrics WHERE is_planned = TRUE")
    planned_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM dod_metrics WHERE is_planned IS FALSE OR is_planned IS NULL")
    actual_count = cur.fetchone()[0]
    cur.execute("SELECT MIN(send_date), MAX(send_date) FROM dod_metrics WHERE is_planned = TRUE")
    pmin, pmax = cur.fetchone()
    cur.close()
    conn.close()

    print(f"\n✅  Done!")
    print(f"   Actual sends  : {actual_count:,} rows")
    print(f"   Planned sends : {planned_count:,} rows  ({pmin} → {pmax})")
    print(f"\n   The calendar now shows planned sends through {FUTURE_END.isoformat()}.")
    print(f"   KPI metrics continue to use actual sends only.")


if __name__ == "__main__":
    main()
