from playwright.sync_api import sync_playwright
configs=[
('homedy','https://homedy.com/ban-nha-rieng','.product-item'),
('alonhadat','https://alonhadat.com.vn/','.item'),
('nhadat24h','https://nhadat24h.net/ban-can-ho-chung-cu','a[href*="-ID"]'),
]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True)
 for name,url,sel in configs:
  print('\n###',name)
  page=b.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36')
  page.goto(url, wait_until='load', timeout=120000); page.wait_for_timeout(3000)
  loc=page.locator(sel)
  n=min(3, loc.count())
  for i in range(n):
   print('\n-- card',i)
   txt=loc.nth(i).inner_text(timeout=5000)
   print(txt[:1200])
   html=loc.nth(i).evaluate("el => el.outerHTML.slice(0,2500)")
   print('HTML:', html)
  page.close()
 b.close()
