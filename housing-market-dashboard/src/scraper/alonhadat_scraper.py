import re

from src.scraper.selenium_scraper import (
    classify_property_type,
    extract_area,
    extract_district,
    extract_listing_date,
    extract_price,
    fetch_page_text,
    normalise_price_text,
    render_listing_cards,
    HANOI_DISTRICTS,
)

ALONHADAT_URL = 'https://alonhadat.com.vn/can-ban-nha-dat/ha-noi'


def _fetch_detail_listing_date(url: str) -> str:
    text = fetch_page_text(url)
    match = re.search(r'Ngày đăng:\s*([^\n\r]+)', text, flags=re.I)
    if match:
        return extract_listing_date(match.group(1))
    return ''


def scrape_alonhadat(progress_cb=None, log_cb=None, abort_event=None):
    records = []
    cards = render_listing_cards(
        ALONHADAT_URL,
        'a.link.vip'
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
        if not title or len(cleaned) < 10:
            continue

        # Alonhadat list cards expose district in .vip-dis, not full street.
        # Use that explicit location instead of falling back to title text.
        address = ' '.join((item.get('address') or '').split())
        district = extract_district(address or cleaned)
        if district not in HANOI_DISTRICTS:
            continue
        price_text = normalise_price_text(item.get('price_text')) or normalise_price_text(cleaned)
        area_text = ' '.join((item.get('area_text') or '').split())
        listing_date = extract_listing_date(item.get('listing_date_text') or cleaned) or _fetch_detail_listing_date(url)

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
            'source': 'alonhadat',
            'url': url,
        })
            if progress_cb:
                progress_cb('alonhadat')
            if log_cb:
                log_cb('alonhadat', 'Success', url)
        except Exception as exc:
            if log_cb:
                log_cb('alonhadat', 'Fail', f"{url} - {exc}")

    return records[:200]
