from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(headless=True); page=b.new_page(user_agent='Mozilla/5.0')
 page.goto('https://alonhadat.com.vn/', wait_until='load', timeout=120000); page.wait_for_timeout(3000)
 for sel in ['.vip .content','.vip-content','.ct_title','.ct_dis','div[class*=content]','.list-property .item','.property']:
  print('\nSEL',sel,'count',page.locator(sel).count())
  for i in range(min(2,page.locator(sel).count())):
   print(page.locator(sel).nth(i).inner_text()[:1000])
   print(page.locator(sel).nth(i).evaluate('el=>el.outerHTML.slice(0,1500)'))
 b.close()
