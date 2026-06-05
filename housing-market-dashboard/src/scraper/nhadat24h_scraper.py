from src.scraper.selenium_scraper import extract_address, extract_area, extract_district, extract_price, render_listing_cards

NHADAT24H_URL = 'https://nhadat24h.net/ban-can-ho-chung-cu'


def scrape_nhadat24h():
    records = []

    # Nhadat24h detail URLs contain an ID suffix.  Using href from the listing
    # anchor avoids the broken guessed/search URLs that caused Flask 404s.
    cards = render_listing_cards(
        NHADAT24H_URL,
        'a[href*="-ID"]:has-text("Tỷ"), a[href*="-ID"]:has-text("tỷ"), a[href*="-ID"]:has-text("triệu"), a[href*="-ID"]:has-text("Triệu")',
    )

    seen_urls = set()
    for item in cards:
        url = item.get('url')
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        cleaned = ' '.join((item.get('text') or '').split())
        title = ' '.join((item.get('title') or cleaned).split())
        if not title or len(cleaned) < 15:
            continue

        address = extract_address(cleaned)
        district = extract_district(cleaned)
        if district == 'Unknown':
            district = extract_district(address)

        records.append({
            'title': title[:120],
            'district': district,
            'address': address,
            'price': extract_price(cleaned),
            'area': extract_area(cleaned),
            'source': 'nhadat24h',
            'url': url,
        })

    return records[:10]
