import os
from seleniumbase import Driver
import time
from bs4 import BeautifulSoup

urls = {
    'alonhadat': 'https://alonhadat.com.vn/can-ban-nha-dat/ha-noi',
    'bds123': 'https://bds123.vn/ban-nha-ha-noi.html',
    'meeyland': 'https://meeyland.com/mua-ban-nha-dat-ha-noi-b42',
    'mogi': 'https://mogi.vn/ha-noi/mua-nha-dat',
    'nhadat24h': 'https://nhadat24h.net/nha-dat-ban-ha-noi',
    'nhaongay': 'https://nhaongay.vn/ban-nha-dat-ha-noi',
    'sosanhnha': 'https://sosanhnha.vn/nha-dat-ban-ha-noi-xc1-ci38',
    'nhatot': 'https://www.nhatot.com/mua-ban-bat-dong-san-ha-noi',
}

driver = Driver(uc=True, headless=True)

with open('c:/Users/Duy/Documents/GitHub/TEC004.2/housing-market-dashboard/scratch_dom2.txt', 'w', encoding='utf-8') as f:
    for name, url in urls.items():
        f.write(f"\n{'='*50}\n{name}: {url}\n{'='*50}\n")
        try:
            driver.get(url)
            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            # remove script and style tags
            for script in soup(["script", "style"]):
                script.extract()
            # print class names of main containers
            content = soup.find('body')
            # To save space, let's just find elements that look like links with prices
            links = content.find_all('a', href=True)
            candidate_cards = []
            for a in links[:100]:
                text = a.get_text().strip()
                if ('tỷ' in text.lower() or 'triệu' in text.lower()) and len(text) > 10:
                    candidate_cards.append((a.get('class', []), text[:100].replace('\n', ' ')))
            f.write("Possible property links classes:\n")
            for c, t in candidate_cards[:5]:
                f.write(f"Class: {c} | Text: {t}\n")
            
            # Or just save the first 2000 chars of body text
            f.write("\nBody text excerpt:\n")
            f.write(content.get_text(separator=' ', strip=True)[:1000])
        except Exception as e:
            f.write(f"Error: {e}")

driver.quit()
