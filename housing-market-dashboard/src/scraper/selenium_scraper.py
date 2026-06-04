import re

from playwright.sync_api import sync_playwright


def render_page(url: str, selector: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        try:
            page.goto(url, wait_until="load", timeout=120000)
            return page.locator(selector).all_inner_texts()
        finally:
            browser.close()


def extract_price(text: str):
    match = re.search(r'(\d+(?:\s\d+)*(?:[.,]\d+)?)\s*(tỷ|triệu|tr)', text, flags=re.I)
    if not match:
        return 0.0
    amount_text = match.group(1).replace(' ', '')
    amount = float(amount_text.replace('.', '').replace(',', '.'))
    unit = match.group(2).lower()
    if unit in ('tỷ', 'ty', 'tr'):
        amount *= 1000
    return round(amount, 2)


def extract_area(text: str):
    match = re.search(r'(\d+(?:[.,]\d+)?)\s*(m2|m²)', text, flags=re.I)
    if not match:
        return 0.0
    return float(match.group(1).replace('.', '').replace(',', '.'))


def extract_district(text: str):
    for pattern in [r'Quận\s[^,|]+', r'Huyện\s[^,|]+', r'TP\.\s[^,|]+', r'Tỉnh\s[^,|]+', r'Phường\s[^,|]+']:
        match = re.search(pattern, text, flags=re.I)
        if match:
            return match.group(0)
    return 'Unknown'
