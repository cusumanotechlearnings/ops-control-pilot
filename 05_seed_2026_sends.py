"""
05_seed_2026_sends.py — Avalon University Marketing Ops AI
Backfills Jan 1, 2026 → Mar 26, 2026 (inclusive) as ACTUAL sends across:

  • dod_metrics         — daily send rows (is_planned = FALSE)
  • voc_responses       — linked responses in the same window
  • automations         — last_run_time updated to Jan–Mar 2026
  • journey_entry_sources — schedule_end_time extended into 2026
  • academic_terms      — Spring 2026 term rows added
  • email_assets        — last_modified_date bumped to 2026 for active assets

Run:
  python 05_seed_2026_sends.py
"""

import os, random, uuid
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from psycopg2.extras import execute_values

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

SEED_START = date(2026, 1, 1)
SEED_END   = date(2026, 3, 26)
UNIV_DOMAIN = "avalon.edu"
UNIV        = "Avalon University"

random.seed(2026)


# ─────────────────────────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────────────────────────

def rand_rate(base, spread=0.03):
    return round(max(0.001, min(0.999, base + random.gauss(0, spread))), 6)


def rand_dt_in_window(start: date = SEED_START, end: date = SEED_END) -> datetime:
    delta = (end - start).days
    d = start + timedelta(days=random.randint(0, delta))
    return datetime(d.year, d.month, d.day, random.randint(6, 18), random.randint(0, 59))


def get_conn():
    return psycopg2.connect(DATABASE_URL)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Academic terms — Spring 2026
# ─────────────────────────────────────────────────────────────────────────────

SPRING_2026_TERMS = [
    ("26SP", "Spring 2026", "2026-01-13", "2026-05-08", "FY2026", "Spring",
     "Undergraduate", "Standard 16-week semester"),
    ("26SP", "Spring 2026", "2026-01-20", "2026-05-01", "FY2026", "Spring",
     "Graduate", "Accelerated 14-week format"),
    ("26SP", "Spring 2026", "2026-01-27", "2026-04-24", "FY2026", "Spring",
     "PhD / Doctoral", "Research-focused, flexible pacing"),
]


def seed_academic_terms(conn):
    print("  Seeding Spring 2026 academic_terms...")
    execute_values(conn.cursor(), """
        INSERT INTO academic_terms
            (term_code, term_name, term_start_date, term_end_date,
             academic_year, season, audience_population, population_notes)
        VALUES %s ON CONFLICT DO NOTHING
    """, SPRING_2026_TERMS)
    conn.commit()


# ─────────────────────────────────────────────────────────────────────────────
# 2. Automations — update last_run_time to 2026 window
# ─────────────────────────────────────────────────────────────────────────────

def update_automations(conn):
    print("  Updating automation last_run_time → Jan–Mar 2026...")
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT automation_id, status FROM automations")
    autos = cur.fetchall()
    updated = 0
    for row in autos:
        new_run = rand_dt_in_window()
        cur.execute(
            "UPDATE automations SET last_run_time = %s WHERE automation_id = %s",
            (new_run, row["automation_id"])
        )
        updated += 1
    conn.commit()
    cur.close()
    print(f"    {updated} automations updated")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Journey entry sources — extend schedule_end_time into 2026
# ─────────────────────────────────────────────────────────────────────────────

def update_journey_entry_sources(conn):
    print("  Updating journey_entry_sources schedule dates → 2026...")
    cur = conn.cursor()
    # Push end dates to Aug 2026 so they overlap the Jan–Mar window
    cur.execute("""
        UPDATE journey_entry_sources
        SET    schedule_end_time = %s
        WHERE  schedule_end_time < %s
    """, (datetime(2026, 8, 31), datetime(2026, 1, 1)))
    updated = cur.rowcount
    # Also make sure active journeys have a start_time in 2026 or earlier
    cur.execute("""
        UPDATE journey_entry_sources
        SET    schedule_start_time = %s
        WHERE  schedule_start_time > %s
    """, (datetime(2025, 9, 1), datetime(2026, 3, 27)))
    conn.commit()
    cur.close()
    print(f"    {updated} entry sources extended")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Email assets — bump last_modified_date to 2026 for some active assets
# ─────────────────────────────────────────────────────────────────────────────

def update_email_assets(conn):
    print("  Bumping email_asset last_modified_date into 2026...")
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT asset_id FROM email_assets")
    asset_ids = [r["asset_id"] for r in cur.fetchall()]
    updated = 0
    for aid in asset_ids:
        new_mod = rand_dt_in_window()
        cur.execute(
            "UPDATE email_assets SET last_modified_date = %s WHERE asset_id = %s",
            (new_mod, aid)
        )
        updated += 1
    conn.commit()
    cur.close()
    print(f"    {updated} email assets updated")


# ─────────────────────────────────────────────────────────────────────────────
# 5. DOD Metrics — actual sends Jan 1 → Mar 26 2026
# ─────────────────────────────────────────────────────────────────────────────

def ensure_is_planned_column(conn):
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
        END $$;
    """)
    conn.commit()
    cur.close()


def load_active_journey_activities(conn):
    """Return all active-journey email activities with send frequency."""
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
    """Per-journey average metrics from historical actual sends."""
    sql = """
        SELECT
            journey_id,
            AVG(open_rate)          AS avg_open_rate,
            AVG(click_rate)         AS avg_click_rate,
            AVG(delivery_rate)      AS avg_delivery_rate,
            AVG(click_to_open_rate) AS avg_ctor,
            AVG(bounce_rate)        AS avg_bounce_rate,
            AVG(total_sends)        AS avg_sends
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
    return dict(row) if row and row["avg_open_rate"] else {
        "avg_open_rate": 0.30, "avg_click_rate": 0.05,
        "avg_delivery_rate": 0.97, "avg_ctor": 0.15,
        "avg_bounce_rate": 0.03, "avg_sends": 800,
    }


def generate_send_dates(start: date, end: date, frequency: str):
    interval = {"Daily": 1, "Weekly": 7, "Monthly": 30, "Once": None}.get(frequency, 7)
    if interval is None:
        yield start
        return
    d = start
    while d <= end:
        yield d
        d += timedelta(days=interval)


def build_metrics_rows(journeys, baselines, fallback):
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
        base_or   = float(b.get("avg_open_rate")    or fallback["avg_open_rate"])
        base_ctr  = float(b.get("avg_click_rate")   or fallback["avg_click_rate"])
        base_dr   = float(b.get("avg_delivery_rate") or fallback["avg_delivery_rate"])
        base_ctor = float(b.get("avg_ctor")          or fallback["avg_ctor"])
        base_br   = float(b.get("avg_bounce_rate")   or fallback["avg_bounce_rate"])
        base_snds = int(float(b.get("avg_sends")     or fallback["avg_sends"]))

        for sd in generate_send_dates(SEED_START, SEED_END, freq):
            sends   = max(10, int(base_snds * random.uniform(0.85, 1.15)))
            deliv   = int(sends * rand_rate(base_dr, 0.01))
            bounces = sends - deliv
            u_opens = int(deliv * rand_rate(base_or, 0.03))
            opens   = int(u_opens / random.uniform(0.70, 0.85))
            u_clk   = int(u_opens * rand_rate(base_ctr * 2, 0.02))
            clicks  = int(u_clk / random.uniform(0.65, 0.80))
            unsubs  = max(0, int(sends * rand_rate(0.002, 0.001)))

            or_c  = round(u_opens / deliv,   6) if deliv  > 0 else 0
            ctr_c = round(u_clk   / deliv,   6) if deliv  > 0 else 0
            dr_c  = round(deliv   / sends,   6) if sends  > 0 else 0
            ctor  = round(u_clk   / u_opens, 6) if u_opens > 0 else 0
            br_c  = round(bounces / sends,   6) if sends  > 0 else 0

            job_id = str(random.randint(5000000, 5999999))

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
                sd, sends, deliv, bounces,
                opens, u_opens, clicks, u_clk, unsubs,
                or_c, ctr_c, dr_c, ctor, br_c,
                audience, dept, audience,
                False,  # is_planned = FALSE → these are actual sends
            ))
    return rows


def insert_metrics(conn, rows):
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


def seed_dod_metrics(conn):
    print("  Seeding dod_metrics Jan 1 – Mar 26 2026 (actual sends)...")
    ensure_is_planned_column(conn)
    journeys  = load_active_journey_activities(conn)
    print(f"    {len(journeys)} active email activities found")
    baselines = load_baselines(conn)
    fallback  = global_fallback(conn)
    rows      = build_metrics_rows(journeys, baselines, fallback)
    print(f"    {len(rows):,} metric rows to insert")
    inserted  = insert_metrics(conn, rows)
    print(f"    {inserted:,} rows inserted")
    return rows  # return so voc_responses can link to them


# ─────────────────────────────────────────────────────────────────────────────
# 6. VOC Responses — linked to Jan–Mar 2026 metric rows
# ─────────────────────────────────────────────────────────────────────────────

VOC_POOL = {
    "positive": [
        ("positive", "email_reply",
         "Really helpful communication — exactly what I needed at this point in the semester. "
         "Thank you for keeping me informed.", 8, False),
        ("positive", "survey",
         "The email was timely and the instructions were clear. "
         "I completed the action the same day I received it.", 9, False),
        ("positive", "web_form",
         "Appreciate the proactive outreach. "
         "Avalon's communication has been outstanding throughout my enrollment.", 8, False),
    ],
    "neutral": [
        ("neutral", "email_reply",
         "Received this email but already took care of it. "
         "Is there anything else I need to do?", None, False),
        ("neutral", "survey",
         "The email was clear but I had a question about the next step. "
         "Could you include a link to the FAQ?", 6, True),
        ("neutral", "web_form",
         "Got the message. Would be helpful to include a phone number "
         "for students who prefer to call.", None, False),
    ],
    "negative": [
        ("negative", "email_reply",
         "I have received this message multiple times. "
         "Please update your records.", None, False),
        ("negative", "survey",
         "The link in this email did not work on my mobile device. "
         "Please test before sending.", 2, True),
        ("negative", "web_form",
         "I am still waiting for a response to my earlier inquiry. "
         "Sending more emails without resolving my issue is frustrating.", 1, True),
    ],
}


def seed_voc_responses(conn, metric_rows):
    print("  Seeding voc_responses linked to 2026 send window...")

    # Fetch the actual DB ids for the rows we just inserted
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT id, email_asset_id, business_unit, target_audience
        FROM   dod_metrics
        WHERE  send_date BETWEEN %s AND %s
          AND  (is_planned IS FALSE OR is_planned IS NULL)
        ORDER  BY RANDOM()
        LIMIT  600
    """, (SEED_START, SEED_END))
    sample = cur.fetchall()

    # Grab a pool of subscriber keys
    cur.execute("SELECT subscriber_key FROM subscribers ORDER BY RANDOM() LIMIT 300")
    sub_keys = [r["subscriber_key"] for r in cur.fetchall()]
    cur.close()

    if not sub_keys:
        print("    No subscribers found — skipping voc_responses")
        return

    sentiments = ["positive", "neutral", "negative"]
    voc_rows = []

    for metric in sample:
        mid    = metric["id"]
        ea_id  = metric["email_asset_id"]
        bu     = metric["business_unit"]
        ta     = metric["target_audience"]
        sk     = random.choice(sub_keys)

        sentiment = random.choice(sentiments)
        tpl = random.choice(VOC_POOL[sentiment])
        sent, channel, text, score, follow_up = tpl

        resp_dt = rand_dt_in_window()
        voc_rows.append((
            sk, ea_id, mid,
            resp_dt, channel, sent, text,
            score,
            sent == "negative" and "unsubscribe" in text.lower(),
            follow_up, None,
            bu, ta
        ))

    execute_values(conn.cursor(), """
        INSERT INTO voc_responses
            (subscriber_key, email_asset_id, dod_metric_id,
             response_date, response_channel, sentiment, response_text,
             survey_score, unsubscribe_request, follow_up_required,
             follow_up_notes, business_unit, target_audience)
        VALUES %s
    """, voc_rows)
    conn.commit()
    print(f"    {len(voc_rows)} voc_responses inserted")


# ─────────────────────────────────────────────────────────────────────────────
# 7. Journeys — bump last_modified_date for active journeys into 2026
# ─────────────────────────────────────────────────────────────────────────────

def update_journeys(conn):
    print("  Bumping active journey last_modified_date into 2026...")
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT journey_id FROM journeys WHERE status = 'Active'")
    jids = [r["journey_id"] for r in cur.fetchall()]
    updated = 0
    for jid in jids:
        new_mod = rand_dt_in_window()
        cur.execute(
            "UPDATE journeys SET last_modified_date = %s WHERE journey_id = %s",
            (new_mod, jid)
        )
        updated += 1
    conn.commit()
    cur.close()
    print(f"    {updated} journeys updated")


# ─────────────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────────────

def verify(conn):
    print("\n── Row count verification ─────────────────────────────────────────")
    cur = conn.cursor()

    checks = [
        ("academic_terms (26SP)",
         "SELECT COUNT(*) FROM academic_terms WHERE term_code = '26SP'"),
        ("dod_metrics (Jan–Mar 2026 actual)",
         "SELECT COUNT(*) FROM dod_metrics "
         "WHERE send_date BETWEEN '2026-01-01' AND '2026-03-26' "
         "  AND (is_planned IS FALSE OR is_planned IS NULL)"),
        ("dod_metrics date range min/max",
         "SELECT MIN(send_date), MAX(send_date) FROM dod_metrics "
         "WHERE is_planned IS FALSE OR is_planned IS NULL"),
        ("voc_responses (Jan–Mar 2026)",
         "SELECT COUNT(*) FROM voc_responses "
         "WHERE response_date BETWEEN '2026-01-01' AND '2026-03-27'"),
        ("automations with last_run 2026",
         "SELECT COUNT(*) FROM automations "
         "WHERE last_run_time >= '2026-01-01'"),
        ("journeys active with modified 2026",
         "SELECT COUNT(*) FROM journeys "
         "WHERE status = 'Active' AND last_modified_date >= '2026-01-01'"),
        ("email_assets with modified 2026",
         "SELECT COUNT(*) FROM email_assets "
         "WHERE last_modified_date >= '2026-01-01'"),
        ("journey_entry_sources covering 2026",
         "SELECT COUNT(*) FROM journey_entry_sources "
         "WHERE schedule_end_time >= '2026-01-01'"),
    ]

    for label, sql in checks:
        cur.execute(sql)
        row = cur.fetchone()
        val = "  ".join(str(v) for v in row) if len(row) > 1 else row[0]
        print(f"  {label:<45}  {val}")

    cur.close()


def main():
    if not DATABASE_URL:
        print("❌  DATABASE_URL not set in .env")
        raise SystemExit(1)

    conn = get_conn()
    print(f"\n🚀  Seeding Jan 1 2026 → Mar 26 2026 across all relevant tables\n")

    print("── Step 1/7  Academic terms ──────────────────────────────────────")
    seed_academic_terms(conn)

    print("── Step 2/7  Automations last_run_time ───────────────────────────")
    update_automations(conn)

    print("── Step 3/7  Journey last_modified_date ──────────────────────────")
    update_journeys(conn)

    print("── Step 4/7  Journey entry source schedule dates ─────────────────")
    update_journey_entry_sources(conn)

    print("── Step 5/7  Email asset last_modified_date ──────────────────────")
    update_email_assets(conn)

    print("── Step 6/7  DOD Metrics (actual sends) ──────────────────────────")
    metric_rows = seed_dod_metrics(conn)

    print("── Step 7/7  VOC Responses ───────────────────────────────────────")
    seed_voc_responses(conn, metric_rows)

    verify(conn)
    conn.close()
    print("\n✅  Done — Jan 1 2026 → Mar 26 2026 populated across all tables.")


if __name__ == "__main__":
    main()
