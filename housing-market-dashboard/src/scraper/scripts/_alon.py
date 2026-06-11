from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(headless=True); page=b.new_page(user_agent='Mozilla/5.0')
 page.goto('https://alonhadat.com.vn/nha-dat/can-ban/nha-dat/1/ha-noi.html', wait_until='load', timeout=120000); page.wait_for_timeout(3000)
 print(page.title())
 for x in page.evaluate("""Array.from(document.querySelectorAll('.content-item, .vipitem, .item')).slice(0,8).map(el=>({text:el.innerText, html:el.outerHTML.slice(0,1500)}))"""):
  print('\nTEXT', x['text'][:800]); print('HTML', x['html'][:800])
 b.close()
