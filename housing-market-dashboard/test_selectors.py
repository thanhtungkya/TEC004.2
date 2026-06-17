import sys
import os

sys.path.append(os.path.abspath('.'))

from src.scraper.selenium_scraper import render_listing_cards

def test():
    tests = {
        'batdongsan': ('https://batdongsan.com.vn/nha-dat-ban-ha-noi', 'a.js__product-link-for-product-id', '.js__card'),
        'bds123': ('https://bds123.vn/ban-nha-ha-noi.html', 'a.bg-white', None),
        'meeyland': ('https://meeyland.com/mua-ban-nha-dat-ha-noi-b42', 'a.flex', '.card-article'),
        'nhadat24h': ('https://nhadat24h.net/nha-dat-ban-ha-noi', '.pn1 a', '.pn1'),
        '123nhadatviet': ('https://123nhadatviet.com/rao-vat/can-ban/nha-dat/t1/ha-noi.html', '.ct_title a', '.item'),
        'nhaongay': ('https://nhaongay.vn/ban-nha-dat-ha-noi', '.card-title a', '.card'),
        'nhatot': ('https://www.nhatot.com/mua-ban-bat-dong-san-ha-noi', 'a', 'li'),
        'sosanhnha': ('https://sosanhnha.vn/nha-dat-ban-ha-noi-xc1-ci38', 'a.js__card-title', None)
    }

    with open('test_new_selectors.txt', 'w', encoding='utf-8') as f:
        for name, (url, sel, c_sel) in tests.items():
            try:
                print(f"Testing {name}...")
                cards = render_listing_cards(url, sel, c_sel)
                f.write(f"{name}: {len(cards)} cards\n")
                if cards:
                    f.write(f"Sample: {cards[0]}\n")
            except Exception as e:
                f.write(f"{name}: error {e}\n")

if __name__ == '__main__':
    test()
