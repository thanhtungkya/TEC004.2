from src.scraper.selenium_scraper import extract_area, extract_district, extract_price, render_page


def scrape_nhadat24h():
    text_blocks = render_page('https://nhadat24h.net/ban-can-ho-chung-cu', "a:has-text('Tỷ')")
    records = []
    for block in text_blocks:
        cleaned = ' '.join(block.split())
        if not cleaned or len(cleaned) < 15:
            continue
        title = cleaned[:120]
        price = extract_price(cleaned)
        area = extract_area(cleaned)
        district = extract_district(cleaned)
        records.append({
            'title': title,
            'district': district,
            'price': price,
            'area': area,
            'source': 'nhadat24h',
        })
    return records[:10]
