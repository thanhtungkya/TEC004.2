from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(headless=True); page=b.new_page(user_agent='Mozilla/5.0')
 page.goto('https://homedy.com/ban-nha-rieng', wait_until='load', timeout=120000); page.wait_for_timeout(3000)
 card=page.locator('.product-item').first
 print(card.inner_text()[:2000])
 print(card.evaluate('''el=>Array.from(el.querySelectorAll("a, h3, .title, [class*=title], .price, .acreage, li.address, .address")).map(x=>({tag:x.tagName, cls:x.className, text:x.innerText, title:x.getAttribute("title"), href:x.href})).slice(0,30)'''))
 b.close()
