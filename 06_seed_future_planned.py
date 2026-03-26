"""
06_seed_future_planned.py — Avalon University Marketing Ops AI
Populates PLANNED / FUTURE data from Mar 27, 2026 → Aug 31, 2026.

Rules enforced:
  • dod_metrics:  is_planned = TRUE
                  total_sends, deliveries, total_bounces, delivery_rate,
                  bounce_rate  → projected from historical baselines
                  opens, clicks, open_rate, click_rate, ctor → NULL
                    (email hasn't sent yet — no engagement data possible)
  • automations:  next_scheduled_run column added & populated (future dates OK)
                  last_run_time NOT changed (already in Jan–Mar 2026 actual window)
  • journeys:     Draft journeys flipped to Active
                  last_modified_date = recent past (not future)
  • journey_entry_sources: schedule_start/end times for newly activated journeys
  • academic_terms: Summer 2026 (Jun–Aug)

Run:
  python 06_seed_future_planned.py
"""

import os, random
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from psycopg2.extras import execute_values

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

PLAN_START = date(2026, 3, 27)
PLAN_END   = date(2026, 8, 31)
TODAY      = date(2026, 3, 25)   # reference "today" for the dataset

UNIV_DOMAIN = "avalon.edu"
UNIV        = "Avalon University"

random.seed(2026_06)


# ─────────────────────────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────────────────────────

def rand_rate(base, spread=0.02):
    return round(max(0.001, min(0.999, base + random.gauss(0, spread))), 6)


def next_date_after(ref: date, frequency: str) -> date:
    """Return the first send date on or after PLAN_START based on frequency."""
    if frequency == "Daily":
        return PLAN_START
    if frequency == "Weekly":
        # next Monday on or after PLAN_START
        days_ahead = (0 - PLAN_START.weekday()) % 7
        return PLAN_START + timedelta(days=days_ahead if days_ahead else 0)
    if frequency == "Monthly":
        # 1st of the month on or after PLAN_START
        if PLAN_START.day == 1:
            return PLAN_START
        return date(PLAN_START.year, PLAN_START.month + 1, 1)
    return PLAN_START  # Once / fallback


def generate_send_dates(start: date, end: date, frequency: str):
    interval = {"Daily": 1, "Weekly": 7, "Monthly": 30, "Once": None}.get(frequency, 7)
    if interval is None:
        yield start
        return
    d = start
    while d <= end:
        yield d
        d += timedelta(days=interval)


def get_conn():
    return psycopg2.connect(DATABASE_URL)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Academic Terms — Summer 2026
# ─────────────────────────────────────────────────────────────────────────────

SUMMER_2026_TERMS = [
    ("26SU", "Summer 2026", "2026-06-01", "2026-08-07", "FY2026", "Summer",
     "Undergraduate", "Condensed 10-week session"),
    ("26SU", "Summer 2026", "2026-06-08", "2026-07-31", "FY2026", "Summer",
     "Graduate", "Condensed 8-week session"),
]


def seed_academic_terms(conn):
    print("  Adding Summer 2026 academic_terms...")
    execute_values(conn.cursor(), """
        INSERT INTO academic_terms
            (term_code, term_name, term_start_date, term_end_date,
             academic_year, season, audience_population, population_notes)
        VALUES %s ON CONFLICT DO NOTHING
    """, SUMMER_2026_TERMS)
    conn.commit()
    print(f"    {len(SUMMER_2026_TERMS)} rows upserted")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Automations — add next_scheduled_run column, populate future dates
# ─────────────────────────────────────────────────────────────────────────────

# Maps the free-text schedule description → (frequency, base_hour)
SCHEDULE_FREQ_MAP = {
    "Daily":   ("Daily",   7),
    "Weekly":  ("Weekly",  8),
    "Monthly": ("Monthly", 7),
    "Once":    ("Once",    9),
}


def parse_frequency(schedule_text: str) -> str:
    """Extract frequency from the free-text schedule field."""
    t = (schedule_text or "").lower()
    if "daily" in t:  return "Daily"
    if "weekly" in t: return "Weekly"
    if "monthly" in t or "1st of month" in t or "15th of month" in t:
        return "Monthly"
    return "Weekly"   # sensible default


def add_next_scheduled_run_column(conn):
    cur = conn.cursor()
    cur.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE  table_name = 'automations'
                AND    column_name = 'next_scheduled_run'
            ) THEN
                ALTER TABLE automations
                ADD COLUMN next_scheduled_run TIMESTAMP;
            END IF;
        END $$;
    """)
    conn.commit()
    cur.close()
    print("    next_scheduled_run column ready")


def update_automations_next_run(conn):
    print("  Populating automations.next_scheduled_run (Apr–Aug 2026)...")
    add_next_scheduled_run_column(conn)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT automation_id, status, schedule FROM automations")
    autos = cur.fetchall()
    updated = 0
    for row in autos:
        freq = parse_frequency(row["schedule"] or "")
        if row["status"] in ("Active",):
            # Next run shortly after Mar 27 2026
            first = next_date_after(PLAN_START, freq)
            # Add a realistic time-of-day offset (6-10 AM)
            hour = {"Daily": 7, "Weekly": 8, "Monthly": 7}.get(freq, 8)
            minute = random.choice([0, 15, 30])
            nsr = datetime(first.year, first.month, first.day, hour, minute)
        elif row["status"] == "Stopped":
            nsr = None
        else:
            # Paused automations — projected restart in May/Jun 2026
            restart_d = date(2026, random.choice([5, 6]),
                             random.randint(1, 28))
            nsr = datetime(restart_d.year, restart_d.month,
                           restart_d.day, 9, 0)
        cur.execute(
            "UPDATE automations SET next_scheduled_run = %s "
            "WHERE automation_id = %s",
            (nsr, row["automation_id"])
        )
        updated += 1
    conn.commit()
    cur.close()
    print(f"    {updated} automations updated")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Activate Draft Journeys + add entry source schedules
# ─────────────────────────────────────────────────────────────────────────────

# Journeys we'll flip from Draft → Active, with a planned launch window
DRAFT_LAUNCHES = {
    "JB-GC-ADM-Graduate-Program-Info": {
        "launch_date": date(2026, 4, 1),
        "frequency": "Monthly",
        "notes": "Graduate inquiry nurture — activated for Fall 2026 recruiting cycle",
    },
}


def activate_draft_journeys(conn):
    print("  Activating Draft journeys with planned start dates...")
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT journey_id, journey_name, status FROM journeys WHERE status = 'Draft'")
    drafts = cur.fetchall()

    activated = 0
    for j in drafts:
        launch_cfg = DRAFT_LAUNCHES.get(j["journey_name"])
        if not launch_cfg:
            continue

        # last_modified_date = a recent PAST date (not future)
        last_mod = datetime(2026, 3, random.randint(10, 25),
                            random.randint(9, 17), random.randint(0, 59))
        cur.execute("""
            UPDATE journeys
            SET    status = 'Active',
                   last_modified_date = %s
            WHERE  journey_id = %s
        """, (last_mod, j["journey_id"]))

        # Upsert entry source schedule
        ld   = launch_cfg["launch_date"]
        freq = launch_cfg["frequency"]
        cur.execute("""
            SELECT entry_source_id FROM journey_entry_sources
            WHERE  journey_id = %s
            LIMIT  1
        """, (j["journey_id"],))
        existing = cur.fetchone()
        if existing:
            cur.execute("""
                UPDATE journey_entry_sources
                SET    schedule_frequency  = %s,
                       schedule_start_time = %s,
                       schedule_end_time   = %s
                WHERE  entry_source_id = %s
            """, (
                freq,
                datetime(ld.year, ld.month, ld.day, 9, 0),
                datetime(2026, 8, 31),
                existing["entry_source_id"]
            ))
        activated += 1

    conn.commit()
    cur.close()
    print(f"    {activated} draft journeys activated")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Journey Entry Sources — extend or add Summer 2026 schedule windows
# ─────────────────────────────────────────────────────────────────────────────

def extend_entry_source_schedules(conn):
    print("  Extending active journey entry source schedule_end_time → Aug 31 2026...")
    cur = conn.cursor()
    cur.execute("""
        UPDATE journey_entry_sources jes
        SET    schedule_end_time = '2026-08-31 23:59:00'
        FROM   journeys j
        WHERE  jes.journey_id = j.journey_id
          AND  j.status = 'Active'
          AND  (jes.schedule_end_time IS NULL OR jes.schedule_end_time < '2026-08-31')
    """)
    updated = cur.rowcount
    conn.commit()
    cur.close()
    print(f"    {updated} entry sources extended to Aug 31 2026")


# ─────────────────────────────────────────────────────────────────────────────
# 5. DOD Metrics — planned sends Mar 27 → Aug 31 2026
#    Engagement metrics (opens, clicks, rates) = NULL (not measurable yet)
#    Delivery-side metrics (sends, deliveries, bounces, dr, br) = projected
# ─────────────────────────────────────────────────────────────────────────────

def load_active_journey_activities(conn):
    sql = """
        SELECT
            j.journey_id,
            j.journey_name,
            j.business_unit,
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


def load_baselines(conn):
    sql = """
        SELECT
            journey_id,
            AVG(delivery_rate)  AS avg_delivery_rate,
            AVG(bounce_rate)    AS avg_bounce_rate,
            AVG(total_sends)    AS avg_sends
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


def global_fallback(conn):
    sql = """
        SELECT
            AVG(delivery_rate) AS avg_delivery_rate,
            AVG(bounce_rate)   AS avg_bounce_rate,
            AVG(total_sends)   AS avg_sends
        FROM dod_metrics
        WHERE is_planned IS FALSE OR is_planned IS NULL
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql)
    row = cur.fetchone()
    cur.close()
    return dict(row) if row and row["avg_sends"] else {
        "avg_delivery_rate": 0.97,
        "avg_bounce_rate": 0.03,
        "avg_sends": 800,
    }


def load_existing_planned_keys(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT email_asset_id, send_date
        FROM   dod_metrics
        WHERE  send_date > %s
          AND  is_planned = TRUE
    """, (TODAY,))
    keys = {(r[0], str(r[1])) for r in cur.fetchall()}
    cur.close()
    return keys


def build_planned_rows(journeys, baselines, fallback, existing_keys):
    rows = []
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
        base_dr   = float(b.get("avg_delivery_rate") or fallback["avg_delivery_rate"])
        base_br   = float(b.get("avg_bounce_rate")   or fallback["avg_bounce_rate"])
        base_snds = int(float(b.get("avg_sends")     or fallback["avg_sends"]))

        start = next_date_after(PLAN_START, freq)

        for sd in generate_send_dates(start, PLAN_END, freq):
            key = (email_id or email_nm, str(sd))
            if key in existing_keys:
                continue

            sends   = max(10, int(base_snds * random.uniform(0.88, 1.12)))
            dr_c    = rand_rate(base_dr, 0.01)
            br_c    = rand_rate(base_br, 0.008)
            deliv   = int(sends * dr_c)
            bounces = sends - deliv

            job_id = str(random.randint(6000000, 6999999))

            rows.append((
                job_id,
                f"{email_nm}{sd.strftime('%b %d %Y')}",
                f"{email_nm}_{job_id}_{sd.strftime('%Y%m%d')}",
                bu, email_nm, email_id,
                jname, jid,
                "Active", 1,
                f"{jid}_1",
                f"{dept.lower()}@{UNIV_DOMAIN}" if dept else f"noreply@{UNIV_DOMAIN}",
                f"{UNIV} {dept}" if dept else UNIV,
                subject,
                sd,
                sends, deliv, bounces,
                # opens / clicks → NULL (future — not measurable)
                None, None, None, None, None,
                # rates: open_rate, click_rate → NULL; delivery_rate, ctor, bounce_rate
                None,   # open_rate
                None,   # click_rate
                round(dr_c, 6),   # delivery_rate — projected
                None,   # click_to_open_rate
                round(br_c, 6),   # bounce_rate — projected
                audience, dept, audience,
                True,   # is_planned
            ))
            existing_keys.add(key)

    return rows


def insert_planned_metrics(conn, rows):
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
    batch = 2000
    inserted = 0
    for i in range(0, len(rows), batch):
        execute_values(cur, sql, rows[i:i+batch])
        conn.commit()
        inserted += cur.rowcount
    cur.close()
    return inserted


def seed_planned_metrics(conn):
    print("  Seeding dod_metrics Mar 27 – Aug 31 2026 (planned, no engagement metrics)...")
    journeys   = load_active_journey_activities(conn)
    print(f"    {len(journeys)} active email activities found")
    baselines  = load_baselines(conn)
    fallback   = global_fallback(conn)
    exist_keys = load_existing_planned_keys(conn)
    rows       = build_planned_rows(journeys, baselines, fallback, exist_keys)
    print(f"    {len(rows):,} planned metric rows generated")
    inserted   = insert_planned_metrics(conn, rows)
    print(f"    {inserted:,} rows inserted")


# ─────────────────────────────────────────────────────────────────────────────
# verification
# ─────────────────────────────────────────────────────────────────────────────

def verify(conn):
    print("\n── Verification ──────────────────────────────────────────────────")
    checks = [
        ("academic_terms (26SU)",
         "SELECT COUNT(*) FROM academic_terms WHERE term_code = '26SU'"),

        ("automations with next_scheduled_run",
         "SELECT COUNT(*) FROM automations WHERE next_scheduled_run IS NOT NULL"),

        ("automations next_scheduled_run range",
         "SELECT MIN(next_scheduled_run), MAX(next_scheduled_run) FROM automations"),

        ("journeys now Active (incl. former Drafts)",
         "SELECT COUNT(*) FROM journeys WHERE status = 'Active'"),

        ("journey_entry_sources through Aug 2026",
         "SELECT COUNT(*) FROM journey_entry_sources "
         "WHERE schedule_end_time >= '2026-08-01'"),

        ("planned dod_metrics (Mar 27–Aug 31 2026)",
         "SELECT COUNT(*) FROM dod_metrics "
         "WHERE is_planned = TRUE AND send_date BETWEEN '2026-03-27' AND '2026-08-31'"),

        ("planned rows — opens NULL check (should = 0 non-null)",
         "SELECT COUNT(*) FROM dod_metrics "
         "WHERE is_planned = TRUE AND send_date >= '2026-03-27' "
         "  AND total_opens IS NOT NULL AND total_opens > 0"),

        ("planned rows — sends projected (should > 0)",
         "SELECT COUNT(*) FROM dod_metrics "
         "WHERE is_planned = TRUE AND send_date >= '2026-03-27' "
         "  AND total_sends > 0"),

        ("planned rows send_date range",
         "SELECT MIN(send_date), MAX(send_date) FROM dod_metrics WHERE is_planned = TRUE"),

        ("actual rows send_date range",
         "SELECT MIN(send_date), MAX(send_date) FROM dod_metrics "
         "WHERE is_planned IS FALSE OR is_planned IS NULL"),

        ("future last_modified_date guard (email_assets > today — should = 0)",
         "SELECT COUNT(*) FROM email_assets WHERE last_modified_date > '2026-03-26'"),

        ("future last_modified_date guard (journeys > today — should = 0)",
         "SELECT COUNT(*) FROM journeys WHERE last_modified_date > '2026-03-26'"),
    ]

    cur = conn.cursor()
    for label, sql in checks:
        cur.execute(sql)
        row = cur.fetchone()
        val = "  ".join(str(v) for v in row) if len(row) > 1 else row[0]
        print(f"  {label:<55}  {val}")
    cur.close()


# ─────────────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    if not DATABASE_URL:
        print("❌  DATABASE_URL not set in .env")
        raise SystemExit(1)

    conn = get_conn()
    print(f"\n🚀  Populating planned/future data Mar 27 → Aug 31 2026\n")

    print("── Step 1/5  Summer 2026 academic terms ──────────────────────────")
    seed_academic_terms(conn)

    print("── Step 2/5  Automations next_scheduled_run ──────────────────────")
    update_automations_next_run(conn)

    print("── Step 3/5  Activate Draft journeys ─────────────────────────────")
    activate_draft_journeys(conn)

    print("── Step 4/5  Extend journey entry source schedules ───────────────")
    extend_entry_source_schedules(conn)

    # dod_metrics intentionally NOT populated for future dates.
    # Future send schedule is represented by journeys, automations,
    # and journey_entry_sources — metric rows only exist for actual sends.

    verify(conn)
    conn.close()
    print("\n✅  Done — planned data through Aug 31 2026 populated.")


if __name__ == "__main__":
    main()
