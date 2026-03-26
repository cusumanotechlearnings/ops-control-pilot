import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()
cur.execute("DELETE FROM dod_metrics WHERE send_date > '2026-03-25'")
print(f"Deleted {cur.rowcount:,} rows with send_date > 2026-03-25")
conn.commit()
cur.execute("SELECT COUNT(*) FROM dod_metrics")
print(f"Remaining: {cur.fetchone()[0]:,} rows")
cur.close()
conn.close()
