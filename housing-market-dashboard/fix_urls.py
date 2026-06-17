import os
import re

scraper_dir = 'c:/Users/Duy/Documents/GitHub/TEC004.2/housing-market-dashboard/src/scraper'

config = {
    'batdongsan': 'https://batdongsan.com.vn/nha-dat-ban-ha-noi',
    'bds123': 'https://bds123.vn/ban-nha-ha-noi.html',
    'meeyland': 'https://meeyland.com/mua-ban-nha-dat-ha-noi-b42',
    'mogi': 'https://mogi.vn/ha-noi/mua-nha-dat',
    'nhadatviet123': 'https://123nhadatviet.com/rao-vat/can-ban/nha-dat/t1/ha-noi.html',
    'nhaongay': 'https://nhaongay.vn/ban-nha-dat-ha-noi',
    'nhatot': 'https://www.nhatot.com/mua-ban-bat-dong-san-ha-noi',
    'sosanhnha': 'https://sosanhnha.vn/nha-dat-ban-ha-noi-xc1-ci38',
}

for source, url in config.items():
    filepath = os.path.join(scraper_dir, f"{source}_scraper.py")
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    var_name = source.upper() + "_URL"
    if source == 'nhadatviet123':
        var_name = "NHADATVIET123_URL"
        content = content.replace("123NHADATVIET_URL", "NHADATVIET123_URL")

    # Replace URL = '...'
    content = re.sub(r"^URL\s*=\s*['\"].*?['\"]", f"{var_name} = '{url}'", content, flags=re.MULTILINE)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Fixed variables")
