import re
import logging

from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)


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


def render_listing_cards(url: str, selector: str, card_selector: str | None = None):
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
                    url: el.href || null
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
