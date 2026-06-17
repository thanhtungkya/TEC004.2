import sys
from pathlib import Path

project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

from src.database.db_connection import get_connection

conn = get_connection()
try:
    cur = conn.cursor()
    cur.execute("SELECT id FROM properties WHERE source='meeyland' AND title LIKE '%(%'")
    rows = cur.fetchall()
    print(f"Found {len(rows)} matching records from meeyland.")
        
    cur.execute("DELETE FROM properties WHERE source='meeyland' AND title LIKE '%(%'")
    conn.commit()
    print(f"Deleted records.")
finally:
    conn.close()
