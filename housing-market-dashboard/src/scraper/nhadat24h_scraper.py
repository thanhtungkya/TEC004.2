import re

from src.scraper.selenium_scraper import (
    classify_property_type,
    extract_area,
    extract_district,
    extract_listing_date,
    extract_price,
    normalise_price_text,
    render_listing_cards,
    HANOI_DISTRICTS,
)

NHADAT24H_URL = 'https://nhadat24h.net/nha-dat-ban-ha-noi'


def scrape_nhadat24h(progress_cb=None, log_cb=None, abort_event=None):
    records = []
    cards = render_listing_cards(
        NHADAT24H_URL,
        '.pn1 a', '.pn1'
    )

    seen_urls = set()
    for item in cards:
        if abort_event and abort_event.is_set():
            break
        url = item.get('url')
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        cleaned = ' '.join((item.get('text') or '').split())
        title = ' '.join((item.get('title') or '').split())
        if not title or len(cleaned) < 15:
            continue

        address = ' '.join((item.get('address') or '').split())
        district = extract_district(address or cleaned)
        if district not in HANOI_DISTRICTS:
            continue
        raw_price = item.get('price_text') or cleaned
        price_text = normalise_price_text(raw_price)
        # Nhadat24h sometimes drops the separator in the compact price element
        # (e.g. "1920 Tỷ" while the title/card says "1,920TỶ"). If that
        # happens, prefer the title/card text so we display "1 tỷ 920 triệu".
        if re.search(r'\b\d{4,}\s*(?:tỷ|ty)\b', price_text, flags=re.I):
            price_text = normalise_price_text(title + ' ' + cleaned)
        area_text = ' '.join((item.get('area_text') or '').split())
        listing_date = extract_listing_date(item.get('listing_date_text') or cleaned)

        try:
            records.append({
            'title': title[:120],
            'district': district,
            'address': address or district,
            'price': extract_price(price_text),
            'price_text': price_text,
            'area': extract_area(area_text or cleaned),
            'area_text': area_text,
            'property_type': classify_property_type(title + ' ' + cleaned, url),
            'listing_date': listing_date,
            'source': 'nhadat24h',
            'url': url,
        })
            if progress_cb:
                progress_cb('nhadat24h')
            if log_cb:
                log_cb('nhadat24h', 'Success', url)
        except Exception as exc:
            if log_cb:
                log_cb('nhadat24h', 'Fail', f"{url} - {exc}")

    return records[:200]
