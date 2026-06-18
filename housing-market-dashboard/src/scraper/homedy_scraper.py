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

HOMEDY_URL = 'https://homedy.com/ban-nha-rieng-ha-noi'


def scrape_homedy(progress_cb=None, log_cb=None, abort_event=None):
    records = []
    cards = render_listing_cards(
        HOMEDY_URL,
        '.product-item-top a[href]', '.product-item'
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
        if not title or len(cleaned) < 20:
            continue

        address = ' '.join((item.get('address') or '').split())
        district = extract_district(address or cleaned)
        if district not in HANOI_DISTRICTS:
            continue
        price_text = normalise_price_text(item.get('price_text')) or normalise_price_text(cleaned)
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
            'source': 'homedy',
            'url': url,
        })
            if progress_cb:
                progress_cb('homedy')
            if log_cb:
                log_cb('homedy', 'Success', url)
        except Exception as exc:
            if log_cb:
                log_cb('homedy', 'Fail', f"{url} - {exc}")

    return records[:200]
