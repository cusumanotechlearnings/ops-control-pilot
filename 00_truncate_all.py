"""
00_truncate_all.py — Avalon University Marketing Ops AI
Deletes ALL rows from every table in the correct order (respecting foreign
key dependencies) so you can re-run 02_seed_data.py against a clean slate.

Run:
  python 00_truncate_all.py
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Tables in dependency order — children before parents
TABLES = [
    "voc_responses",
    "dod_metrics",
    "opportunities",
    "subscribers",
    "journey_activities",
    "journey_entry_sources",
    "automation_activities",
    "journeys",
    "automations",
    "sql_queries",
    "image_assets",
    "content_block_assets",
    "landing_page_assets",
    "sms_assets",
    "email_assets",
    "academic_terms",
]


def run():
    if not DATABASE_URL:
        print("❌  DATABASE_URL not set in .env")
        raise SystemExit(1)

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    print("Truncating all tables...\n")
    for table in TABLES:
        try:
            cur.execute(f"DELETE FROM {table}")
            count = cur.rowcount
            conn.commit()
            print(f"  ✓  {table}: {count:,} rows deleted")
        except Exception as e:
            conn.rollback()
            print(f"  ⚠  {table}: {e}")

    cur.close()
    conn.close()
    print("\n✅ Done. Run 02_seed_data.py to repopulate.")


if __name__ == "__main__":
    run()
