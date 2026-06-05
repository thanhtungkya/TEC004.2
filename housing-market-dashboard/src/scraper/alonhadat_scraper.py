from src.scraper.selenium_scraper import extract_address, extract_area, extract_district, extract_price, render_listing_cards

ALONHADAT_URL = 'https://alonhadat.com.vn/'


def scrape_alonhadat():
    records = []

    # Alonhadat listing detail links are normal .html anchors.  The homepage has
    # both featured-listing anchors and later anchors with class="link"; keep
    # only hrefs that look like actual listing detail pages.
    cards = render_listing_cards(
        ALONHADAT_URL,
        'a[href$=".html"]:has-text("tỷ"), a[href$=".html"]:has-text("Tỷ"), a[href$=".html"]:has-text("triệu"), a[href$=".html"]:has-text("Triệu")',
    )

    seen_urls = set()
    for item in cards:
        url = item.get('url')
        if not url or url in seen_urls or '/tin-tuc-' in url or '/dang-tin-' in url:
            continue
        seen_urls.add(url)

        cleaned = ' '.join((item.get('text') or '').split())
        title = ' '.join((item.get('title') or cleaned).split())
        if not title or len(cleaned) < 10:
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
            'source': 'alonhadat',
            'url': url,
        })

    return records[:10]
