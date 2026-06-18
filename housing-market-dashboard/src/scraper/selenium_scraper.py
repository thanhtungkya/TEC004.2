import re
import logging
from datetime import date, timedelta
import time
import random
from typing import Optional

from seleniumbase import Driver
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)

HANOI_DISTRICTS = {
    'Ba Đình', 'Hoàn Kiếm', 'Tây Hồ', 'Long Biên', 'Cầu Giấy', 'Đống Đa',
    'Hai Bà Trưng', 'Hoàng Mai', 'Thanh Xuân', 'Sóc Sơn', 'Đông Anh', 'Gia Lâm',
    'Nam Từ Liêm', 'Thanh Trì', 'Bắc Từ Liêm', 'Mê Linh', 'Hà Đông', 'Sơn Tây',
    'Ba Vì', 'Phúc Thọ', 'Đan Phượng', 'Hoài Đức', 'Quốc Oai', 'Thạch Thất',
    'Chương Mỹ', 'Thanh Oai', 'Thường Tín', 'Phú Xuyên', 'Ứng Hòa', 'Mỹ Đức'
}


def _get_driver():
    """Return a patched SeleniumBase driver."""
    return Driver(uc=True, headless=True)


def render_page(url: str, selector: str):
    """
    Launch an undetected Chromium browser via SeleniumBase, navigate to *url*,
    and return the inner-text of every element matching *selector*.
    """
    driver = None
    try:
        driver = _get_driver()
        driver.get(url)
        time.sleep(random.uniform(2.5, 4.5))              # human-like pause
        els = driver.find_elements(By.CSS_SELECTOR, selector)
        texts = [el.text for el in els]
        return texts
    except Exception as exc:
        logger.error("render_page(%s) failed: %s", url, exc)
        return []                                         # graceful fallback
    finally:
        try:
            if driver:
                driver.quit()
        except Exception:
            pass


def fetch_page_text(url: str) -> str:
    """Fetch rendered page body text for detail-page metadata extraction."""
    driver = None
    try:
        driver = _get_driver()
        driver.get(url)
        time.sleep(random.uniform(2.5, 4.5))
        return driver.find_element(By.TAG_NAME, "body").text
    except Exception as exc:
        logger.error("fetch_page_text(%s) failed: %s", url, exc)
        return ""
    finally:
        try:
            if driver:
                driver.quit()
        except Exception:
            pass


def render_listing_cards(url: str, selector: str, card_selector: Optional[str] = None):
    """
    Return listing data from anchors matching *selector*.

    For real-estate sites, the detail URL is the anchor's real href.  The
    readable card text is often stored on a parent element, so callers may pass
    *card_selector* to collect the full listing card text while keeping the
    exact anchor href.
    """
    driver = None
    try:
        driver = _get_driver()
        driver.get(url)
        time.sleep(random.uniform(3.0, 5.5))
        
        js_code = """
        const els = Array.from(document.querySelectorAll(arguments[0]));
        const cardSelector = arguments[1];
        return els.map(el => {
            const card = cardSelector ? el.closest(cardSelector) : null;
            const textNode = card || el;
            const fullText = (textNode.innerText || textNode.textContent || '').trim();

            // --- Price extraction ---
            // Try known CSS selectors first
            let price = '';
            const priceEl = textNode.querySelector('.price, .a-txt-cl1, .vip-price, [class*=price], .gia, [class*=gia]');
            if (priceEl) {
                price = priceEl.innerText.replace(/^Giá:\\s*/i, '').trim();
            }
            // Regex fallback on fullText if CSS found nothing
            if (!price) {
                const pm = fullText.match(/(\\d+(?:[\\s.,]\\d+)*)\\s*(tỷ|ty|triệu|tr)\\b(?!\\s*(?:\\/|trên)\\s*m)/i);
                if (pm) price = pm[0].trim();
            }

            // --- Area extraction ---
            let area = '';
            const areaEl = textNode.querySelector('.acreage, .a-txt-cl2, .vip-kt, .acr, [class*=acreage], [class*=area], .dien-tich');
            if (areaEl) {
                area = areaEl.innerText.replace(/^DT:\\s*/i, '').replace(/[·•]/g, '').trim();
            }
            if (!area) {
                // Regex: look for a number directly followed by m²/m2 (not part of "70Mx5T")
                const am = fullText.match(/(\\d{1,5}(?:[.,]\\d{1,2})?)\\s*(?:m2|m²)(?!\\w)/i);
                if (am) area = am[0].trim();
            }

            return {
                text: fullText,
                title: (el.innerText || el.textContent || '').trim(),
                url: el.href || null,
                price_text: price,
                area_text: area,
                address: (textNode.querySelector('li.address')?.getAttribute('title') || textNode.querySelector('.rvVitri span, .vip-dis, .address, .caption .address, p.address, .location')?.innerText || '').trim(),
                listing_date_text: (textNode.querySelector('.date, .time, [class*=date], [class*=time]')?.innerText || '').trim()
            };
        });
        """
        results = driver.execute_script(js_code, selector, card_selector)
        return results if results else []
    except Exception as exc:
        logger.error("render_listing_cards(%s) failed: %s", url, exc)
        return []
    finally:
        try:
            if driver:
                driver.quit()
        except Exception:
            pass


def _parse_vietnamese_amount(amount_text: str, unit: str) -> float:
    clean = str(amount_text or '').strip()
    parts = clean.split(' ')
    if len(parts) > 1 and (',' in parts[-1] or '.' in parts[-1]):
        clean = parts[-1]

    compact = clean.replace(' ', '')
    unit = (unit or '').lower()
    if unit in ('tỷ', 'ty'):
        # Listing sites often write 1 920 tỷ / 1.920 tỷ / 1,920 tỷ to mean
        # 1 tỷ 920 triệu, not one-thousand-nine-hundred-twenty tỷ.
        if re.match(r'^\d+[\s.,]\d{3}$', clean):
            compact = re.sub(r'[\s,]', '.', clean)
        else:
            compact = compact.replace(',', '.')
    else:
        compact = compact.replace('.', '').replace(',', '.')
    return float(compact)


def normalise_price_text(text: str):
    """Extract and normalise the first Vietnamese price from *text*.

    Returns a clean, human-readable price string like '8 tỷ 250 triệu'
    or '' when no price can be extracted.
    NEVER returns raw/unstructured text.
    """
    raw = ' '.join(str(text or '').split()).strip()
    if not raw:
        return ''
    lowered = raw.lower()
    if 'thỏa' in lowered or 'thoả' in lowered:
        return 'Thỏa thuận'

    match = re.search(r'(\d+(?:[\s.,]\d+)*)\s*(tỷ|ty|triệu|tr)\b(?!\s*(?:/|trên)\s*(?:m|th|tháng))', raw, flags=re.I)
    if not match:
        # No recognisable Vietnamese price pattern found – return empty
        # instead of dumping the raw text into the price column.
        return ''

    amount = match.group(1).strip()
    unit = match.group(2).lower()
    
    parts = amount.split(' ')
    if len(parts) > 1 and (',' in parts[-1] or '.' in parts[-1]):
        amount = parts[-1]

    if unit in ('triệu', 'tr'):
        return f"{amount.replace('.', ',')} triệu"

    # Keep the unit text, but avoid UI like "8.25 tỷ".  Vietnamese listing
    # users expect "8 tỷ 250 triệu" for decimal-billion prices.
    try:
        value = _parse_vietnamese_amount(amount, unit)
    except ValueError:
        return f"{amount} tỷ"
    whole = int(value)
    million = round((value - whole) * 1000)
    if million <= 0:
        return f"{whole} tỷ"
    if million >= 1000:
        return f"{whole + 1} tỷ"
    return f"{whole} tỷ {million} triệu"


def extract_price(text: str):
    clean_text = str(text or '')
    if 'thỏa' in clean_text.lower() or 'thoả' in clean_text.lower():
        return 0.0

    total = 0.0
    found = False
    for match in re.finditer(r'(\d+(?:\s\d+)*(?:[.,]\d+)?)\s*(tỷ|ty|triệu|tr)\b(?!\s*(?:/|trên)\s*(?:m|th|tháng))', clean_text, flags=re.I):
        found = True
        amount_text = match.group(1)
        unit = match.group(2).lower()
        amount = _parse_vietnamese_amount(amount_text, unit)
        if unit in ('tỷ', 'ty'):
            total += amount * 1000
        else:
            total += amount
    return round(total, 2) if found else 0.0


def extract_area(text: str):
    """Extract area in m² from *text*.

    Matches real area patterns like '150 m²', '65.5m2', '66M²', 'DT 70m', '70Mx5T'.
    Smartly extracts isolated formats like '58m' if context suggests it's an area,
    but avoids facade sizes or distances like 'Mặt tiền 5m' or 'Cách ô tô 20m'.
    Returns 0.0 when no valid area is found.
    """
    if not text:
        return 0.0

    def _parse_area_number(s: str) -> float:
        """Parse a number that may use . or , as decimal or thousands sep."""
        s = s.strip()
        if ',' in s:
            s = s.replace(',', '.')
        parts = s.split('.')
        if len(parts) == 2 and len(parts[1]) == 3:
            return float(parts[0] + parts[1])
        return float(s)

    # 1. Standard: number directly followed by m² / m2.
    m1 = re.search(r'(?<!\d)(\d{1,5}(?:[.,]\d{1,2})?)\s*(?:m2|m²)(?!\w)', text, flags=re.I)
    if m1:
        val = _parse_area_number(m1.group(1))
        if 5 <= val <= 10000: return val

    # 2. Prefix: 'Diện tích', 'DT', 'Dtich', 'S' followed by a number and an optional 'm'
    m2 = re.search(r'(?:diện tích|dtich|dt|s)\s*:?\s*(\d{1,5}(?:[.,]\d{1,2})?)\s*m?(?!\w)', text, flags=re.I)
    if m2:
        val = _parse_area_number(m2.group(1))
        if 5 <= val <= 10000: return val

    # 3. Multiplier: '70Mx5T' or '70m x 5 tầng'
    m3 = re.search(r'(?<!\d)(\d{1,5}(?:[.,]\d{1,2})?)\s*m\s*[x\*]\s*\d+\s*(?:T|tầng)', text, flags=re.I)
    if m3:
        val = _parse_area_number(m3.group(1))
        if 5 <= val <= 10000: return val

    # 4. Dangerous Fallback: catch isolated \d+m if it's reasonably large (>= 15)
    # and not preceded by facade/distance words ('mt', 'mặt tiền', 'ngõ', 'đường', 'cách', 'rộng', 'sâu')
    m4 = re.search(r'(?<!\d)(\d{2,5}(?:[.,]\d{1,2})?)\s*m\b', text, flags=re.I)
    if m4:
        val = _parse_area_number(m4.group(1))
        idx = m4.start()
        context_before = text[max(0, idx-20):idx].lower()
        avoid_words = ['mt', 'tiền', 'ngõ', 'đường', 'cách', 'rộng', 'sâu', 'vào']
        if not any(w in context_before for w in avoid_words):
            if 15 <= val <= 10000:
                return val

    return 0.0


def extract_district(text: str):
    if not text:
        return 'Unknown'
    text_lower = text.lower()
    for d in HANOI_DISTRICTS:
        if d.lower() in text_lower:
            return d
    return 'Unknown'


def classify_property_type(text: str, url: str = '') -> str:
    value = f"{text or ''} {url or ''}".lower()
    apartment_markers = [
        'căn hộ', 'can-ho', 'chung cư', 'chung-cu', 'apartment', 'ccmn',
        'tòa tháp', 'toa-thap', 'pn', 'phòng ngủ'
    ]
    land_markers = [
        'đất', 'dat-', 'nha-dat', 'nhà đất', 'bán đất', 'ban-dat',
        'mặt tiền', 'mat-tien', 'nhà phố', 'nha-pho', 'biệt thự', 'biet-thu',
        'nhà riêng', 'nha-rieng', 'thổ cư', 'tho-cu', 'lô đất', 'lo-dat'
    ]
    if any(marker in value for marker in apartment_markers):
        return 'Apartment'
    if any(marker in value for marker in land_markers):
        return 'Land'
    # Requirement only allows Apartment/Land. Prefer Land for generic house/land listings.
    return 'Land'


def extract_listing_date(text: str, crawl_date: Optional[date] = None) -> str:
    value = ' '.join(str(text or '').split()).strip()
    today = crawl_date or date.today()
    lowered = value.lower()
    if not value:
        return ''
    if 'hôm nay' in lowered:
        return today.isoformat()
    if 'hôm qua' in lowered:
        return (today - timedelta(days=1)).isoformat()
    match = re.search(r'(\d+)\s+ngày\s+trước', lowered, flags=re.I)
    if match:
        return (today - timedelta(days=int(match.group(1)))).isoformat()

    match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', value)
    if match:
        day, month, year = (int(part) for part in match.groups())
        if year < 100:
            year += 2000
        try:
            return date(year, month, day).isoformat()
        except ValueError:
            return value[:40]

    match = re.search(r'(\d{1,2})\s+tháng\s+(\d{1,2})(?:\s*,?\s*(\d{4}))?', lowered, flags=re.I)
    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3) or today.year)
        try:
            return date(year, month, day).isoformat()
        except ValueError:
            return ''

    return ''


def extract_address(text: str):
    """Best-effort address extraction from Vietnamese listing text."""
    patterns = [
        r'(?:Địa chỉ|Khu vực|Vị trí)\s*:?\s*([^|]+)',
        r'((?:Phường|P\.?|Đường|Ngõ|Quận|Q\.?|Huyện|H\.?)\s[^|]+)',
        r'([^|]*(?:Đống Đa|Ba Đình|Hoàn Kiếm|Hai Bà Trưng|Thanh Xuân|Cầu Giấy|Tây Hồ|Hoàng Mai|Long Biên|Hà Đông|Nam Từ Liêm|Bắc Từ Liêm|Đông Anh|Gia Lâm|Hoài Đức|Thanh Trì)[^|]*)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            address = (match.group(1) if match.lastindex else match.group(0)).strip(' ,.-–—|')
            return address[:180] if address else 'Unknown'

    # Nhadat24h search-card snippets often contain the usable location only
    # in the title (project/street name) and not as a formal address field.
    compact = ' '.join(text.split()).strip(' ,.-–—|')
    return compact[:180] if compact else 'Unknown'
