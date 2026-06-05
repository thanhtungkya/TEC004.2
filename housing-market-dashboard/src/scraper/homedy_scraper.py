from src.scraper.selenium_scraper import extract_address, extract_area, extract_district, extract_price, render_listing_cards

HOMEDY_URL = 'https://homedy.com/ban-nha-rieng'


def scrape_homedy():
    records = []

    # Homedy detail anchors use an -es<ID> suffix and class image-thumb on the
    # cards observed from the site.  Pull the anchor href directly instead of
    # reconstructing a URL from title text.
    cards = render_listing_cards(
        HOMEDY_URL,
        'a.image-thumb[href*="-es"], a[href*="-es"]:has-text("tỷ"), a[href*="-es"]:has-text("Tỷ"), a[href*="-es"]:has-text("triệu"), a[href*="-es"]:has-text("Triệu")',
        '.product-item',
    )

    seen_urls = set()
    for item in cards:
        url = item.get('url')
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        cleaned = ' '.join((item.get('text') or '').split())
        title = ' '.join((item.get('title') or cleaned).split())
        if not title or len(cleaned) < 20:
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
            'source': 'homedy',
            'url': url,
        })

    return records[:10]
