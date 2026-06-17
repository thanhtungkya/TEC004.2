import os
import re

scraper_dir = 'c:/Users/Duy/Documents/GitHub/TEC004.2/housing-market-dashboard/src/scraper'

# url, selector, card_selector
config = {
    'alonhadat': ('https://alonhadat.com.vn/can-ban-nha-dat/ha-noi', 'a.link.vip', None),
    'bds123': ('https://bds123.vn/ban-nha-ha-noi.html', 'a.bg-white', None),
    'homedy': ('https://homedy.com/ban-nha-rieng-ha-noi', '.product-item-top a[href]', '.product-item'),
    'meeyland': ('https://meeyland.com/mua-ban-nha-dat-ha-noi-b42', 'a.bg-white', None),
    'mogi': ('https://mogi.vn/ha-noi/mua-nha-dat', 'a.link-overlay', '.property-item'),
    'nhadat24h': ('https://nhadat24h.net/nha-dat-ban-ha-noi', '.property-item a, .item a', '.property-item, .item'),
    'nhadatviet123': ('https://123nhadatviet.com/rao-vat/can-ban/nha-dat/t1/ha-noi.html', '.item a', '.item'),
    'nhaongay': ('https://nhaongay.vn/ban-nha-dat-ha-noi', '.property-item a', '.property-item'),
    'nhatot': ('https://www.nhatot.com/mua-ban-bat-dong-san-ha-noi', 'li.AdItem_wrapperAdItem__1hEwM a, li a.cqzlgv9', 'li'),
    'sosanhnha': ('https://sosanhnha.vn/nha-dat-ban-ha-noi-xc1-ci38', 'a.js__card-title, a.pr-title', '.vipZero, .property-list'),
    'batdongsan': ('https://batdongsan.com.vn/nha-dat-ban-ha-noi', 'a.pr-title', '.product-item'),
}

for source, (url, selector, card_selector) in config.items():
    filepath = os.path.join(scraper_dir, f"{source}_scraper.py")
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Replace the URL
    content = re.sub(r"[A-Z0-9_]+_URL\s*=\s*['\"].*?['\"]", f"{source.upper()}_URL = '{url}'", content)

    # 2. Update the function signature
    # def scrape_alonhadat(progress_cb=None, abort_event=None): -> def scrape_alonhadat(progress_cb=None, log_cb=None, abort_event=None):
    content = re.sub(rf"def scrape_{source}\(progress_cb=None, abort_event=None\):", f"def scrape_{source}(progress_cb=None, log_cb=None, abort_event=None):", content)

    # 3. Update the render_listing_cards call
    # render_listing_cards( URL, selector, card_selector )
    card_arg = f", '{card_selector}'" if card_selector else ""
    # Find the render_listing_cards(...) block and replace it
    # Since it might span multiple lines, let's use a regex that handles it
    content = re.sub(r"render_listing_cards\([\s\S]*?\)", f"render_listing_cards(\n        {source.upper()}_URL,\n        '{selector}'{card_arg}\n    )", content)

    # 4. Implement try/catch and log_cb in the loop
    # We will find the `for item in cards:` block
    # and replace the inside logic
    
    # We don't want to completely rewrite the extraction logic if it's customized, 
    # but the logic is mostly the same in all generated scrapers.
    # Let's inject try/except inside the loop, and the log_cb.
    
    # Actually, the loop contains:
    #         if abort_event and abort_event.is_set():
    #             break
    #         ...
    #         records.append({...})
    #         if progress_cb:
    #             progress_cb(...)
    
    # Let's replace the `records.append(...)` up to `progress_cb(...)` with the new logic.
    
    append_pattern = r"records\.append\(\{(.*?)\}\)\s*if progress_cb:\s*progress_cb\('[^']+'\)"
    match = re.search(append_pattern, content, flags=re.DOTALL)
    if match:
        dict_content = match.group(1)
        replacement = f"""try:
            records.append({{{dict_content}}})
            if progress_cb:
                progress_cb('{source}')
            if log_cb:
                log_cb('{source}', 'Success', url)
        except Exception as exc:
            if log_cb:
                log_cb('{source}', 'Fail', f"{{url}} - {{exc}}")"""
        content = content[:match.start()] + replacement + content[match.end():]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
print("Done updating scrapers.")
