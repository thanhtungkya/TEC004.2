import json
import sqlite3
import sys
from pathlib import Path

project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

from src.database.db_connection import get_connection

conn = get_connection()
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("""
    SELECT source, id, url, title, area, area_text, price_text
    FROM properties
    WHERE area = 70.0 OR area_text LIKE '%70%'
    LIMIT 20
""")
rows = cur.fetchall()
data = [dict(r) for r in rows]

with open('scratch_70m2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

conn.close()
