import sys
from pathlib import Path

project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

from src.database.db_connection import get_connection

conn = get_connection()
try:
    cur = conn.cursor()
    # Get one 70m2 property for each source
    cur.execute("""
        SELECT * FROM (
            SELECT source, id, url, title, area, area_text,
                   ROW_NUMBER() OVER(PARTITION BY source ORDER BY id DESC) as rn
            FROM properties
            WHERE area = 70.0 AND area_text = ''
        ) WHERE rn = 1
    """)
    rows = cur.fetchall()
    for row in rows:
        print(row["source"], row["url"], row["title"][:50])
finally:
    conn.close()
