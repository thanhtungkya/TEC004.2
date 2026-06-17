import json
import sys
from pathlib import Path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))
from src.database.db_connection import get_connection

conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT source, id, url, title, area, area_text, price_text FROM properties WHERE title LIKE '%Tạ Hiện%'")
rows = cur.fetchall()
data = [dict(r) for r in rows]

with open('scratch_ta_hien.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
conn.close()
