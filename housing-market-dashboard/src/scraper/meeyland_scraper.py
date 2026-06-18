import re
from src.scraper.selenium_scraper import (
    classify_property_type, extract_area, extract_district,
    extract_listing_date, extract_price, normalise_price_text,
    render_listing_cards, HANOI_DISTRICTS
)

MEEYLAND_URL = 'https://meeyland.com/mua-ban-nha-dat-ha-noi-b42'

# Meeyland property detail URLs always end with a purely numeric ID segment.
# e.g. https://meeyland.com/mua-ban-nha-dat/.../123456
# Category / district pages like /mua-ban-nha-dat-ha-noi-b42 must be excluded.
_MEEYLAND_PROPERTY_RE = re.compile(r'/\d+$')


def scrape_meeyland(progress_cb=None, log_cb=None, abort_event=None):
    records = []
    cards = render_listing_cards(
        MEEYLAND_URL,
        '.card-article a[href]', '.card-article'
    )
    seen_urls = set()
    for item in cards:
        if abort_event and abort_event.is_set(): break
        url = item.get('url')
        if not url or url in seen_urls: continue

        # Only keep individual property pages (URL path ends with /digits)
        from urllib.parse import urlparse
        path = urlparse(url).path.rstrip('/')
        if not _MEEYLAND_PROPERTY_RE.search(path):
            continue

        seen_urls.add(url)
        cleaned = ' '.join((item.get('text') or '').split())
        title = ' '.join((item.get('title') or '').split())
        if not title or len(cleaned) < 10: continue
        
        # Explicitly ignore aggregate category links like "Bán nhà đất Thanh Xuân (3.427)"
        if re.search(r'Bán nhà đất .*\([\d\.]+\)', title, re.IGNORECASE):
            continue
            
        address = ' '.join((item.get('address') or '').split())
        district = extract_district(address or cleaned)
        if district not in HANOI_DISTRICTS: continue
        price_text = normalise_price_text(item.get('price_text')) or normalise_price_text(cleaned)
        area_text = ' '.join((item.get('area_text') or '').split())
        listing_date = extract_listing_date(item.get('listing_date_text') or cleaned)
        try:
            records.append({
                'title': title[:120], 'district': district, 'address': address or district,
                'price': extract_price(price_text), 'price_text': price_text,
                'area': extract_area(area_text or cleaned), 'area_text': area_text,
                'property_type': classify_property_type(title + ' ' + cleaned, url),
                'listing_date': listing_date, 'source': 'meeyland', 'url': url,
            })
            if progress_cb:
                progress_cb('meeyland')
            if log_cb:
                log_cb('meeyland', 'Success', url)
        except Exception as exc:
            if log_cb:
                log_cb('meeyland', 'Fail', f"{url} - {exc}")
    return records[:200]
