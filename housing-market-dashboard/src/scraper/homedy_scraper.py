from src.scraper.selenium_scraper import extract_area, extract_district, extract_price, render_page


def scrape_homedy():
    text_blocks = render_page('https://homedy.com/ban-nha-rieng', '.product-item')
    records = []
    for block in text_blocks:
        cleaned = ' '.join(block.split())
        if not cleaned or len(cleaned) < 20:
            continue
        title = cleaned.split('Tỷ')[0].split('Triệu')[0].strip(' |')
        price = extract_price(cleaned)
        area = extract_area(cleaned)
        district = extract_district(cleaned)
        records.append({
            'title': title[:120],
            'district': district,
            'price': price,
            'area': area,
            'source': 'homedy',
        })
    return records[:10]
