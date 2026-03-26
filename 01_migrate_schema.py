"""
01_migrate_schema.py — Avalon University Marketing Ops AI
Run this ONCE before 02_seed_data.py to bring the existing Neon tables
up to the schema that 02_seed_data.py expects.

Idempotent: safe to re-run. Uses ADD COLUMN IF NOT EXISTS everywhere.

Run:
  python 01_migrate_schema.py
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

MIGRATIONS = [

    # ── academic_terms ──────────────────────────────────────────────────────
    "ALTER TABLE academic_terms ADD COLUMN IF NOT EXISTS audience_population VARCHAR",
    "ALTER TABLE academic_terms ADD COLUMN IF NOT EXISTS population_notes    VARCHAR",

    # ── email_assets ────────────────────────────────────────────────────────
    "ALTER TABLE email_assets ADD COLUMN IF NOT EXISTS legacy_id             VARCHAR",
    "ALTER TABLE email_assets ADD COLUMN IF NOT EXISTS unique_id             VARCHAR",
    "ALTER TABLE email_assets ADD COLUMN IF NOT EXISTS asset_type_name       VARCHAR",
    "ALTER TABLE email_assets ADD COLUMN IF NOT EXISTS asset_type_id         VARCHAR",
    "ALTER TABLE email_assets ADD COLUMN IF NOT EXISTS target_audience        VARCHAR",
    "ALTER TABLE email_assets ADD COLUMN IF NOT EXISTS copy_found            TEXT",
    "ALTER TABLE email_assets ADD COLUMN IF NOT EXISTS ampscript              TEXT",
    "ALTER TABLE email_assets ADD COLUMN IF NOT EXISTS images                TEXT",
    "ALTER TABLE email_assets ADD COLUMN IF NOT EXISTS urls_found            TEXT",
    "ALTER TABLE email_assets ADD COLUMN IF NOT EXISTS emails_found          TEXT",
    "ALTER TABLE email_assets ADD COLUMN IF NOT EXISTS content_blocks        TEXT",
    "ALTER TABLE email_assets ADD COLUMN IF NOT EXISTS created_by_email      VARCHAR",
    "ALTER TABLE email_assets ADD COLUMN IF NOT EXISTS last_modified_by_email VARCHAR",
    "ALTER TABLE email_assets ADD COLUMN IF NOT EXISTS object_id             VARCHAR",

    # ── image_assets ────────────────────────────────────────────────────────
    "ALTER TABLE image_assets ADD COLUMN IF NOT EXISTS file_size_kb         INTEGER",
    "ALTER TABLE image_assets ADD COLUMN IF NOT EXISTS width_px             INTEGER",
    "ALTER TABLE image_assets ADD COLUMN IF NOT EXISTS height_px            INTEGER",
    "ALTER TABLE image_assets ADD COLUMN IF NOT EXISTS campaign_name        VARCHAR",
    "ALTER TABLE image_assets ADD COLUMN IF NOT EXISTS email_subject_line   VARCHAR",
    "ALTER TABLE image_assets ADD COLUMN IF NOT EXISTS last_used_date       DATE",
    "ALTER TABLE image_assets ADD COLUMN IF NOT EXISTS image_description    TEXT",

    # ── sms_assets ──────────────────────────────────────────────────────────
    "ALTER TABLE sms_assets ADD COLUMN IF NOT EXISTS target_audience        VARCHAR",
    "ALTER TABLE sms_assets ADD COLUMN IF NOT EXISTS country_code           VARCHAR",
    "ALTER TABLE sms_assets ADD COLUMN IF NOT EXISTS opt_in_configured      BOOLEAN",
    "ALTER TABLE sms_assets ADD COLUMN IF NOT EXISTS created_by_name        VARCHAR",
    "ALTER TABLE sms_assets ADD COLUMN IF NOT EXISTS created_by_email       VARCHAR",
    "ALTER TABLE sms_assets ADD COLUMN IF NOT EXISTS last_modified_by_name  VARCHAR",
    "ALTER TABLE sms_assets ADD COLUMN IF NOT EXISTS last_modified_by_email VARCHAR",

    # ── content_block_assets ────────────────────────────────────────────────
    "ALTER TABLE content_block_assets ADD COLUMN IF NOT EXISTS unique_id              VARCHAR",
    "ALTER TABLE content_block_assets ADD COLUMN IF NOT EXISTS asset_type_name        VARCHAR",
    "ALTER TABLE content_block_assets ADD COLUMN IF NOT EXISTS folder_id              VARCHAR",
    "ALTER TABLE content_block_assets ADD COLUMN IF NOT EXISTS version                VARCHAR",
    "ALTER TABLE content_block_assets ADD COLUMN IF NOT EXISTS ampscript              TEXT",
    "ALTER TABLE content_block_assets ADD COLUMN IF NOT EXISTS images                TEXT",
    "ALTER TABLE content_block_assets ADD COLUMN IF NOT EXISTS urls_found            TEXT",
    "ALTER TABLE content_block_assets ADD COLUMN IF NOT EXISTS created_by_name       VARCHAR",
    "ALTER TABLE content_block_assets ADD COLUMN IF NOT EXISTS created_by_email      VARCHAR",
    "ALTER TABLE content_block_assets ADD COLUMN IF NOT EXISTS last_modified_by_name  VARCHAR",
    "ALTER TABLE content_block_assets ADD COLUMN IF NOT EXISTS last_modified_by_email VARCHAR",

    # ── landing_page_assets ─────────────────────────────────────────────────
    "ALTER TABLE landing_page_assets ADD COLUMN IF NOT EXISTS unique_id               VARCHAR",
    "ALTER TABLE landing_page_assets ADD COLUMN IF NOT EXISTS target_audience          VARCHAR",
    "ALTER TABLE landing_page_assets ADD COLUMN IF NOT EXISTS asset_type_name         VARCHAR",
    "ALTER TABLE landing_page_assets ADD COLUMN IF NOT EXISTS folder                  VARCHAR",
    "ALTER TABLE landing_page_assets ADD COLUMN IF NOT EXISTS version                 VARCHAR",
    "ALTER TABLE landing_page_assets ADD COLUMN IF NOT EXISTS copy_found              TEXT",
    "ALTER TABLE landing_page_assets ADD COLUMN IF NOT EXISTS has_google_tag_manager  BOOLEAN",
    "ALTER TABLE landing_page_assets ADD COLUMN IF NOT EXISTS created_by_name         VARCHAR",
    "ALTER TABLE landing_page_assets ADD COLUMN IF NOT EXISTS created_by_email        VARCHAR",
    "ALTER TABLE landing_page_assets ADD COLUMN IF NOT EXISTS last_modified_by_name   VARCHAR",
    "ALTER TABLE landing_page_assets ADD COLUMN IF NOT EXISTS last_modified_by_email  VARCHAR",

    # ── automations ─────────────────────────────────────────────────────────
    "ALTER TABLE automations ADD COLUMN IF NOT EXISTS automation_key       VARCHAR",
    "ALTER TABLE automations ADD COLUMN IF NOT EXISTS description          TEXT",
    "ALTER TABLE automations ADD COLUMN IF NOT EXISTS target_audience       VARCHAR",
    "ALTER TABLE automations ADD COLUMN IF NOT EXISTS type_id              INTEGER",
    "ALTER TABLE automations ADD COLUMN IF NOT EXISTS status_id            INTEGER",
    "ALTER TABLE automations ADD COLUMN IF NOT EXISTS category_id          INTEGER",
    "ALTER TABLE automations ADD COLUMN IF NOT EXISTS last_run_instance_id VARCHAR",

    # ── journeys ────────────────────────────────────────────────────────────
    "ALTER TABLE journeys ADD COLUMN IF NOT EXISTS journey_key            VARCHAR",
    "ALTER TABLE journeys ADD COLUMN IF NOT EXISTS description            TEXT",
    "ALTER TABLE journeys ADD COLUMN IF NOT EXISTS workflow_api_version   FLOAT",
    "ALTER TABLE journeys ADD COLUMN IF NOT EXISTS event_definition_id   VARCHAR",
    "ALTER TABLE journeys ADD COLUMN IF NOT EXISTS target_audience_detail VARCHAR",

    # ── journey_entry_sources ───────────────────────────────────────────────
    "ALTER TABLE journey_entry_sources ADD COLUMN IF NOT EXISTS journey_name          VARCHAR",
    "ALTER TABLE journey_entry_sources ADD COLUMN IF NOT EXISTS business_unit         VARCHAR",
    "ALTER TABLE journey_entry_sources ADD COLUMN IF NOT EXISTS event_definition_key  VARCHAR",
    "ALTER TABLE journey_entry_sources ADD COLUMN IF NOT EXISTS event_definition_id   VARCHAR",
    "ALTER TABLE journey_entry_sources ADD COLUMN IF NOT EXISTS data_extension_id     VARCHAR",
    "ALTER TABLE journey_entry_sources ADD COLUMN IF NOT EXISTS target_audience        VARCHAR",
    "ALTER TABLE journey_entry_sources ADD COLUMN IF NOT EXISTS mode                  VARCHAR",
    "ALTER TABLE journey_entry_sources ADD COLUMN IF NOT EXISTS schedule_occurrences  INTEGER",
    "ALTER TABLE journey_entry_sources ADD COLUMN IF NOT EXISTS created_by            VARCHAR",
    "ALTER TABLE journey_entry_sources ADD COLUMN IF NOT EXISTS last_modified_by      VARCHAR",

    # ── journey_activities ──────────────────────────────────────────────────
    "ALTER TABLE journey_activities ADD COLUMN IF NOT EXISTS activity_key        VARCHAR",
    "ALTER TABLE journey_activities ADD COLUMN IF NOT EXISTS activity_description TEXT",
    "ALTER TABLE journey_activities ADD COLUMN IF NOT EXISTS email_pre_header   VARCHAR",
    "ALTER TABLE journey_activities ADD COLUMN IF NOT EXISTS send_key           VARCHAR",
    "ALTER TABLE journey_activities ADD COLUMN IF NOT EXISTS triggered_send_id  VARCHAR",
    "ALTER TABLE journey_activities ADD COLUMN IF NOT EXISTS salesforce_tracking BOOLEAN",
    "ALTER TABLE journey_activities ADD COLUMN IF NOT EXISTS send_logging        BOOLEAN",
    "ALTER TABLE journey_activities ADD COLUMN IF NOT EXISTS click_tracking      BOOLEAN",
    "ALTER TABLE journey_activities ADD COLUMN IF NOT EXISTS target_audience     VARCHAR",
    "ALTER TABLE journey_activities ADD COLUMN IF NOT EXISTS last_modified_by    VARCHAR",

    # ── subscribers ─────────────────────────────────────────────────────────
    "ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS colleague_id        VARCHAR",
    "ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS email               VARCHAR",
    "ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS first_name          VARCHAR",
    "ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS last_name           VARCHAR",
    "ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS preferred_first_name VARCHAR",
    "ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS target_audience      VARCHAR",
    "ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS original_campus      VARCHAR",
    "ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS term_start_date      TIMESTAMP",
    "ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS popsel_name          VARCHAR",

    # ── opportunities ───────────────────────────────────────────────────────
    "ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS colleague_id   VARCHAR",
    "ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS target_audience VARCHAR",

    # ── dod_metrics — extra columns + auto-increment id for voc_responses ──
    "ALTER TABLE dod_metrics ADD COLUMN IF NOT EXISTS id_combo                VARCHAR",
    "ALTER TABLE dod_metrics ADD COLUMN IF NOT EXISTS unique_email_send        VARCHAR",
    "ALTER TABLE dod_metrics ADD COLUMN IF NOT EXISTS journey_version          INTEGER",
    "ALTER TABLE dod_metrics ADD COLUMN IF NOT EXISTS unique_journey_id_version VARCHAR",
    "ALTER TABLE dod_metrics ADD COLUMN IF NOT EXISTS sender_name              VARCHAR",
    "ALTER TABLE dod_metrics ADD COLUMN IF NOT EXISTS target_audience           VARCHAR",
    # id column used by voc_responses (handled separately below via DO block)

    # ── NEW TABLE: sql_queries ───────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS sql_queries (
        query_definition_id  VARCHAR PRIMARY KEY,
        name                 VARCHAR,
        key                  VARCHAR,
        target_name          VARCHAR,
        target_key           VARCHAR,
        target_id            VARCHAR,
        target_description   TEXT,
        target_update_type_id   INTEGER,
        target_update_type_name VARCHAR,
        category_id          INTEGER,
        is_frozen            BOOLEAN,
        business_unit        VARCHAR,
        query_text           TEXT,
        created_date         TIMESTAMP,
        modified_date        TIMESTAMP
    )
    """,

    # ── NEW TABLE: automation_activities ────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS automation_activities (
        activity_id                  VARCHAR PRIMARY KEY,
        automation_id                VARCHAR,
        automation_key               VARCHAR,
        automation_name              VARCHAR,
        activity_step                INTEGER,
        activity_name                VARCHAR,
        activity_description         TEXT,
        activity_object_type_id      INTEGER,
        target_data_extension_id     VARCHAR,
        target_data_extension_key    VARCHAR,
        activity_data_extension_name VARCHAR,
        business_unit                VARCHAR
    )
    """,

    # ── NEW TABLE: voc_responses ─────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS voc_responses (
        id                  BIGSERIAL PRIMARY KEY,
        subscriber_key      VARCHAR,
        email_asset_id      VARCHAR,
        dod_metric_id       BIGINT,
        response_date       TIMESTAMP,
        response_channel    VARCHAR,
        sentiment           VARCHAR,
        response_text       TEXT,
        survey_score        INTEGER,
        unsubscribe_request BOOLEAN,
        follow_up_required  BOOLEAN,
        follow_up_notes     TEXT,
        business_unit       VARCHAR,
        target_audience     VARCHAR
    )
    """,
]

# dod_metrics needs an integer id column that voc_responses references.
# SERIAL can't use ADD COLUMN IF NOT EXISTS, so we use a DO block.
ADD_DOD_ID = """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'dod_metrics' AND column_name = 'id'
    ) THEN
        ALTER TABLE dod_metrics ADD COLUMN id BIGSERIAL;
    END IF;
END
$$;
"""


def run():
    if not DATABASE_URL:
        print("❌  DATABASE_URL not set in .env")
        raise SystemExit(1)

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    total = len(MIGRATIONS) + 1
    ok = 0

    for i, sql in enumerate(MIGRATIONS, 1):
        label = sql.strip().splitlines()[0][:80]
        try:
            cur.execute(sql)
            conn.commit()
            print(f"  [{i}/{total}] ✓  {label}")
            ok += 1
        except Exception as e:
            conn.rollback()
            print(f"  [{i}/{total}] ⚠  {label}")
            print(f"           {e}")

    # dod_metrics id column
    try:
        cur.execute(ADD_DOD_ID)
        conn.commit()
        print(f"  [{total}/{total}] ✓  dod_metrics id BIGSERIAL (if not exists)")
        ok += 1
    except Exception as e:
        conn.rollback()
        print(f"  [{total}/{total}] ⚠  dod_metrics id column: {e}")

    cur.close()
    conn.close()
    print(f"\n{'✅' if ok == total else '⚠️ '} Migration complete: {ok}/{total} statements succeeded.")
    if ok == total:
        print("   You can now run:  backend/venv/bin/python 02_seed_data.py")


if __name__ == "__main__":
    run()
