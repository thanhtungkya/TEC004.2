from src.scraper.selenium_scraper import extract_area, extract_district, extract_price, normalise_price_text, render_listing_cards

ALONHADAT_URL = 'https://alonhadat.com.vn/'


def scrape_alonhadat():
    records = []
    cards = render_listing_cards(
        ALONHADAT_URL,
        '.vip-properties .vip-title a[href$=".html"]',
        '.vip-properties article.item',
    )

    seen_urls = set()
    for item in cards:
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
            'source': 'alonhadat',
            'url': url,
        })

    return records[:10]
