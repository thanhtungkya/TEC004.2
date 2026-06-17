import sys
import os
import json

sys.path.append(os.path.abspath('.'))

from seleniumbase import Driver
from selenium.webdriver.common.by import By
import time

urls = {
    'batdongsan': 'https://batdongsan.com.vn/nha-dat-ban-ha-noi',
    'bds123': 'https://bds123.vn/ban-nha-ha-noi.html',
    'meeyland': 'https://meeyland.com/mua-ban-nha-dat-ha-noi-b42',
    'nhadat24h': 'https://nhadat24h.net/nha-dat-ban-ha-noi',
    '123nhadatviet': 'https://123nhadatviet.com/rao-vat/can-ban/nha-dat/t1/ha-noi.html',
    'nhaongay': 'https://nhaongay.vn/ban-nha-dat-ha-noi',
    'nhatot': 'https://www.nhatot.com/mua-ban-bat-dong-san-ha-noi',
    'sosanhnha': 'https://sosanhnha.vn/nha-dat-ban-ha-noi-xc1-ci38'
}

def analyze():
    results = {}
    driver = Driver(uc=True, headless=True)
    try:
        for name, url in urls.items():
            print(f"Visiting {name}...")
            driver.get(url)
            time.sleep(5)
            
            # Find elements that look like property links (they usually contain numbers like price or area)
            js = """
            return Array.from(document.querySelectorAll('a')).map(a => ({
                href: a.href,
                text: a.innerText.trim(),
                className: a.className,
                parentClass: a.parentElement ? a.parentElement.className : ''
            })).filter(a => a.text.length > 20 && (a.text.includes('tỷ') || a.text.includes('triệu') || a.text.includes('m2') || /\d/.test(a.text))).slice(0, 5);
            """
            links = driver.execute_script(js)
            results[name] = links
    finally:
        driver.quit()
        
    with open('dom_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    analyze()
