import json
import sys
from src.scraper.selenium_scraper import render_listing_cards, normalise_price_text

def test_scraper(url, sel1, sel2):
    cards = render_listing_cards(url, sel1, sel2)
    with open("scratch_output.txt", "a", encoding="utf-8") as f:
        f.write(f"URL: {url}\n")
        for i, c in enumerate(cards[:2]):
            f.write(f"Card {i+1}:\n")
            f.write(f"  Title: {c.get('title')}\n")
            f.write(f"  Price text (JS): {c.get('price_text')}\n")
            f.write(f"  Price text (Python): {normalise_price_text(c.get('price_text') or c.get('text'))}\n")
            f.write(f"  Full text: {c.get('text')}\n")
            f.write("-" * 40 + "\n")

if __name__ == "__main__":
    with open("scratch_output.txt", "w", encoding="utf-8") as f:
        f.write("")
    test_scraper('https://homedy.com/ban-nha-rieng-ha-noi', '.product-item-top a[href]', '.product-item')
    test_scraper('https://meeyland.com/mua-ban-nha-dat-ha-noi-b42', '.card-article a[href]', '.card-article')
    test_scraper('https://nhadat24h.net/nha-dat-ban', '.a-title', '.property-item')
