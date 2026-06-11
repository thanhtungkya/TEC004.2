from src.database.create_tables import create_tables
from src.database.db_connection import get_connection
from src.database.property_repository import PropertyRepository
from src.scraper.scraper_manager import run_all_scrapers

create_tables()
results = run_all_scrapers(['alonhadat', 'homedy', 'nhadat24h'])
rows=[]
seen=set()
for source, items in results.items():
    for item in items or []:
        url=(item.get('url') or '').strip()
        if not url or url in seen:
            continue
        seen.add(url)
        rows.append({
            'title': (item.get('title') or 'Untitled listing').strip()[:120],
            'district': (item.get('district') or 'Unknown').strip(),
            'address': (item.get('address') or item.get('district') or 'Unknown').strip(),
            'price': item.get('price') or 0,
            'price_text': item.get('price_text') or '',
            'area': item.get('area') or 0,
            'area_text': item.get('area_text') or '',
            'property_type': item.get('property_type') or 'Land',
            'listing_date': item.get('listing_date') or '',
            'source': source,
            'url': url,
        })

conn=get_connection()
try:
    conn.execute('DELETE FROM properties')
    conn.commit()
finally:
    conn.close()

if rows:
    PropertyRepository().insert_many(rows)
print(f'refreshed rows={len(rows)}')
for row in rows[:8]:
    print(row['source'], '|', row['title'], '|', row['address'], '|', row['price_text'], '|', row['area_text'], '|', row['property_type'], '|', row['listing_date'])
