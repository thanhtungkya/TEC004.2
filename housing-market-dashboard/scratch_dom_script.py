import os
from seleniumbase import Driver
import time

urls = {
    'alonhadat': ('https://alonhadat.com.vn/can-ban-nha-dat/ha-noi', '.vip-properties article.item'),
    'bds123': ('https://bds123.vn/ban-nha-ha-noi.html', '.item'),
    'homedy': ('https://homedy.com/ban-nha-rieng-ha-noi', '.product-item'),
    'meeyland': ('https://meeyland.com/mua-ban-nha-dat-ha-noi-b42', '.listing-item, .card'),
    'mogi': ('https://mogi.vn/ha-noi/mua-nha-dat', '.property-item'),
    'nhadat24h': ('https://nhadat24h.net/nha-dat-ban-ha-noi', '.property-item, .item'),
    'nhadatviet123': ('https://123nhadatviet.com/rao-vat/can-ban/nha-dat/t1/ha-noi.html', '.item'),
    'nhaongay': ('https://nhaongay.vn/ban-nha-dat-ha-noi', '.property-item'),
    'nhatot': ('https://www.nhatot.com/mua-ban-bat-dong-san-ha-noi', 'li.AdItem_wrapperAdItem__1hEwM, li'),
    'sosanhnha': ('https://sosanhnha.vn/nha-dat-ban-ha-noi-xc1-ci38', '.property-list, .item')
}

driver = Driver(uc=True, headless=True)

with open('c:/Users/Duy/Documents/GitHub/TEC004.2/housing-market-dashboard/scratch_dom.txt', 'w', encoding='utf-8') as f:
    for name, (url, selector) in urls.items():
        f.write(f"\n{'='*50}\n{name}: {url}\n{'='*50}\n")
        try:
            driver.get(url)
            time.sleep(3)
            # Find the first element that matches the selector
            els = driver.find_elements("css selector", selector)
            if els:
                f.write(els[0].get_attribute("outerHTML"))
            else:
                f.write("No elements found using selector.")
        except Exception as e:
            f.write(f"Error: {e}")

driver.quit()
