from src.scraper.selenium_scraper import extract_area, extract_district, extract_price, normalise_price_text, render_listing_cards

HOMEDY_URL = 'https://homedy.com/ban-nha-rieng'


def scrape_homedy():
    records = []
    cards = render_listing_cards(
        HOMEDY_URL,
        '.product-item a.title[href*="-es"]',
        '.product-item',
    )

    seen_urls = set()
    for item in cards:
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
        price_text = normalise_price_text(item.get('price_text') or cleaned)
        area_text = ' '.join((item.get('area_text') or '').split())

        records.append({
            'title': title[:120],
            'district': district,
            'address': address or district,
            'price': extract_price(price_text),
            'price_text': price_text,
            'area': extract_area(area_text or cleaned),
            'area_text': area_text,
            'source': 'homedy',
            'url': url,
        })

    return records[:10]
