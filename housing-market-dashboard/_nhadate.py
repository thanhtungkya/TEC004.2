from src.scraper.selenium_scraper import render_listing_cards
xs=render_listing_cards('https://nhadat24h.net/ban-can-ho-chung-cu','.dv-item .dv-txt a[href*="-ID"]','.dv-item')
for x in xs[5:10]:
 print('---')
 print(x['text'][:500])
