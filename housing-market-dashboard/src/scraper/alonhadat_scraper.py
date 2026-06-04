from src.scraper.selenium_scraper import extract_area, extract_district, extract_price, render_page


def scrape_alonhadat():
    text_blocks = render_page('https://alonhadat.com.vn/', '.item')
    records = []
    for block in text_blocks:
        cleaned = ' '.join(block.split())
        if not cleaned or len(cleaned) < 10:
            continue
        title = cleaned.split('Giá:')[0].split('DT:')[0].strip(' |')
        price = extract_price(cleaned)
        area = extract_area(cleaned)
        district = extract_district(cleaned)
        records.append({
            'title': title[:120],
            'district': district,
            'price': price,
            'area': area,
            'source': 'alonhadat',
        })
    return records[:10]
