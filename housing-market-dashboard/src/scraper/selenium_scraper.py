import re
import logging
from datetime import date, timedelta
from typing import Optional

from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

HANOI_DISTRICTS = {
    'Ba Đình', 'Hoàn Kiếm', 'Tây Hồ', 'Long Biên', 'Cầu Giấy', 'Đống Đa',
    'Hai Bà Trưng', 'Hoàng Mai', 'Thanh Xuân', 'Sóc Sơn', 'Đông Anh', 'Gia Lâm',
    'Nam Từ Liêm', 'Thanh Trì', 'Bắc Từ Liêm', 'Mê Linh', 'Hà Đông', 'Sơn Tây',
    'Ba Vì', 'Phúc Thọ', 'Đan Phượng', 'Hoài Đức', 'Quốc Oai', 'Thạch Thất',
    'Chương Mỹ', 'Thanh Oai', 'Thường Tín', 'Phú Xuyên', 'Ứng Hòa', 'Mỹ Đức'
}


def _new_page(browser):
    return browser.new_page(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        )
    )


def render_page(url: str, selector: str):
    """
    Launch a headless Chromium browser via Playwright, navigate to *url*,
    and return the inner-text of every element matching *selector*.

    On Windows the Playwright event-loop can clash with Flask's reloader
    (``--debug``), so we guard every step with explicit error handling and
    keep the browser life-cycle as short as possible.
    """
    pw = None
    browser = None
    try:
        pw = sync_playwright().start()
        browser = pw.chromium.launch(headless=True)
        page = _new_page(browser)
        page.goto(url, wait_until="load", timeout=120_000)
        page.wait_for_timeout(2000)                       # let JS render
        texts = page.locator(selector).all_inner_texts()
        return texts
    except Exception as exc:
        logger.error("render_page(%s) failed: %s", url, exc)
        return []                                         # graceful fallback
    finally:
        try:
            if browser:
                browser.close()
        except Exception:
            pass
        try:
            if pw:
                pw.stop()
        except Exception:
            pass


def fetch_page_text(url: str) -> str:
    """Fetch rendered page body text for detail-page metadata extraction."""
    pw = None
    browser = None
    try:
        pw = sync_playwright().start()
        browser = pw.chromium.launch(headless=True)
        page = _new_page(browser)
        page.goto(url, wait_until="load", timeout=120_000)
        page.wait_for_timeout(2000)
        return page.locator("body").inner_text(timeout=10_000)
    except Exception as exc:
        logger.error("fetch_page_text(%s) failed: %s", url, exc)
        return ""
    finally:
        try:
            if browser:
                browser.close()
        except Exception:
            pass
        try:
            if pw:
                pw.stop()
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
    pw = None
    browser = None
    try:
        pw = sync_playwright().start()
        browser = pw.chromium.launch(headless=True)
        page = _new_page(browser)
        page.goto(url, wait_until="load", timeout=120_000)
        page.wait_for_timeout(3000)
        return page.locator(selector).evaluate_all(
            """
            (els, cardSelector) => els.map(el => {
                const card = cardSelector ? el.closest(cardSelector) : null;
                const textNode = card || el;
                return {
                    text: (textNode.innerText || textNode.textContent || '').trim(),
                    title: (el.innerText || el.textContent || '').trim(),
                    url: el.href || null,
                    price_text: (textNode.querySelector('.price, .a-txt-cl1, .vip-price, [class*=price]')?.innerText || '').replace(/^Giá:\\s*/i, '').trim(),
                    area_text: (textNode.querySelector('.acreage, .a-txt-cl2, .vip-kt, .acr, [class*=acreage]')?.innerText || '').replace(/^DT:\\s*/i, '').trim(),
                    address: (textNode.querySelector('li.address')?.getAttribute('title') || textNode.querySelector('.rvVitri span, .vip-dis, .address, .caption .address, p.address')?.innerText || '').trim(),
                    listing_date_text: (textNode.querySelector('.date, .time, [class*=date], [class*=time]')?.innerText || '').trim()
                };
            })
            """,
            card_selector,
        )
    except Exception as exc:
        logger.error("render_listing_cards(%s) failed: %s", url, exc)
        return []
    finally:
        try:
            if browser:
                browser.close()
        except Exception:
            pass
        try:
            if pw:
                pw.stop()
        except Exception:
            pass


def _parse_vietnamese_amount(amount_text: str, unit: str) -> float:
    clean = str(amount_text or '').strip()
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
    raw = ' '.join(str(text or '').split()).strip()
    if not raw:
        return ''
    lowered = raw.lower()
    if 'thỏa' in lowered or 'thoả' in lowered:
        return 'Thỏa thuận'

    match = re.search(r'(\d+(?:[\s.,]\d+)*)\s*(tỷ|ty|triệu|tr)\b', raw, flags=re.I)
    if not match:
        return raw

    amount = match.group(1).strip()
    unit = match.group(2).lower()
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
    for match in re.finditer(r'(\d+(?:\s\d+)*(?:[.,]\d+)?)\s*(tỷ|ty|triệu|tr)\b', clean_text, flags=re.I):
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
    match = re.search(r'(\d+(?:[.,]\d+)?)\s*(m2|m²)', text, flags=re.I)
    if not match:
        return 0.0
    return float(match.group(1).replace('.', '').replace(',', '.'))


def extract_district(text: str):
    for pattern in [
        r'(?:Quận|Huyện|Thành phố|\bTP\.?)\s*[^,|\-–—]+',
        r'Đống Đa|Ba Đình|Hoàn Kiếm|Hai Bà Trưng|Thanh Xuân|Cầu Giấy|Tây Hồ|Hoàng Mai|Long Biên|Hà Đông|Nam Từ Liêm|Bắc Từ Liêm|Đông Anh|Gia Lâm|Hoài Đức|Thanh Trì',
        r'Tỉnh\s[^,|\-–—]+',
        r'Phường\s[^,|\-–—]+',
    ]:
        match = re.search(pattern, text, flags=re.I)
        if match:
            return match.group(0).strip()
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
