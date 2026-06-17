import sys
from pathlib import Path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

from src.database.db_connection import get_connection
from src.scraper.selenium_scraper import extract_area, normalise_price_text

conn = get_connection()
conn.row_factory = __import__('sqlite3').Row
try:
    cur = conn.cursor()
    cur.execute("SELECT id, title, area_text, price_text FROM properties")
    rows = cur.fetchall()
    
    updated = 0
    for row in rows:
        row_id = row['id']
        title = row['title']
        old_area_text = row['area_text'] or ''
        
        # New area extraction logic
        new_area = extract_area(old_area_text)
        if new_area == 0.0 and title:
            new_area = extract_area(title)
            
        cur.execute("UPDATE properties SET area = ? WHERE id = ?", (new_area, row_id))
        updated += 1
        
    conn.commit()
    print(f"Successfully cleaned and updated {updated} records with new algorithms.")
finally:
    conn.close()
