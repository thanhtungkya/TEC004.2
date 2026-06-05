from src.scraper.selenium_scraper import render_listing_cards
specs=[
('homedy','https://homedy.com/ban-nha-rieng','.product-item a.title[href*="-es"]','.product-item'),
('nhadat24h','https://nhadat24h.net/ban-can-ho-chung-cu','.dv-item .dv-txt a[href*="-ID"]','.dv-item'),
('alon','https://alonhadat.com.vn/','.vip-properties .vip-title a[href$=".html"]','.vip-properties article.item'),
]
for name,url,sel,card in specs:
 print('\n---',name)
 xs=render_listing_cards(url,sel,card)
 print('count',len(xs))
 for x in xs[:3]:
  print(x)
