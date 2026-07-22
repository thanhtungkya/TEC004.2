import re

from src.scraper.selenium_scraper import (
    classify_property_type,
    extract_area,
    extract_district,
    extract_price,
    normalise_price_text,
    collect_cards_from_sources,
    SCRAPE_LINK_LIMIT,
    HANOI_DISTRICTS,
)

NHADAT24H_URL = 'https://nhadat24h.net/nha-dat-ban-ha-noi'
NHADAT24H_URLS = [
    'https://nhadat24h.net/nha-dat-ban-ha-noi',
    'https://nhadat24h.net/ban-can-ho-chung-cu-ha-noi',
    'https://nhadat24h.net/ban-nha-rieng-ha-noi',
    'https://nhadat24h.net/ban-dat-ha-noi',
]


def scrape_nhadat24h(progress_cb=None, log_cb=None, abort_event=None, existing_urls=None, link_limit=SCRAPE_LINK_LIMIT):
    records = []
    cards = collect_cards_from_sources(
        'nhadat24h',
        NHADAT24H_URLS,
        '.pn1 a', '.pn1',
        existing_urls=existing_urls,
        limit=link_limit,
        log_cb=log_cb,
        abort_event=abort_event,
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
        price_text = normalise_price_text(item.get('price_text')) or normalise_price_text(cleaned)
        # Nhadat24h sometimes drops the separator in the compact price element
        # (e.g. "1920 Tỷ" while the title/card says "1,920TỶ"). If that
        # happens, prefer the title/card text so we display "1 tỷ 920 triệu".
        if re.search(r'\b\d{4,}\s*(?:tỷ|ty)\b', price_text, flags=re.I):
            price_text = normalise_price_text(title + ' ' + cleaned)
        area_text = ' '.join((item.get('area_text') or '').split())

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
            'listing_date': '',
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

    return records[:link_limit]
