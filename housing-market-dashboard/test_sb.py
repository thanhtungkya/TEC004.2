import sys
sys.path.append("c:/Users/Duy/Documents/GitHub/TEC004.2/housing-market-dashboard")

from src.scraper.selenium_scraper import render_listing_cards

url = "https://batdongsan.com.vn/nha-dat-ban-ha-noi"
cards = render_listing_cards(url, "a.pr-title", ".product-item")
print(f"Found {len(cards)} cards on batdongsan.com.vn")
if cards:
    print(cards[0])
