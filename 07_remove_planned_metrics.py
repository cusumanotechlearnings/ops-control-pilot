"""
07_remove_planned_metrics.py
Removes all dod_metrics rows where is_planned = TRUE.

Future send planning is represented by journeys, automations,
and journey_entry_sources — not by pre-populated metric rows.
"""
import os, psycopg2
from dotenv import load_dotenv
load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM dod_metrics WHERE is_planned = TRUE")
before = cur.fetchone()[0]
print(f"Planned rows before:  {before:,}")

cur.execute("DELETE FROM dod_metrics WHERE is_planned = TRUE")
deleted = cur.rowcount
conn.commit()
print(f"Deleted:              {deleted:,}")

cur.execute("SELECT COUNT(*) FROM dod_metrics WHERE is_planned = TRUE")
after = cur.fetchone()[0]
print(f"Planned rows after:   {after:,}")

cur.execute("SELECT COUNT(*), MIN(send_date), MAX(send_date) FROM dod_metrics")
row = cur.fetchone()
print(f"Remaining total rows: {row[0]:,}  ({row[1]} → {row[2]})")

cur.close()
conn.close()
print("\n✅  Done — dod_metrics now contains actual sends only.")
