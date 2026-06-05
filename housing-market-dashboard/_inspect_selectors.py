from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(headless=True)
 page=b.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36')
 page.goto('https://nhadat24h.net/ban-can-ho-chung-cu', wait_until='load', timeout=120000); page.wait_for_timeout(3000)
 print('nhadat cards')
 js="""
 Array.from(document.querySelectorAll('a[href*="-ID"]')).slice(0,20).map(a=>{
   const card=a.closest('.dv-txt, .item, .dv-item, li, .dv-box') || a.parentElement;
   return {href:a.href,title:a.getAttribute('title')||a.innerText, cardText:(card&&card.innerText||'').trim().slice(0,800), html:(card&&card.outerHTML||a.outerHTML).slice(0,2000)}
 })
 """
 for x in page.evaluate(js):
  print('\nURL',x['href']); print('TITLE',x['title']); print('TEXT',x['cardText']); print('HTML',x['html'][:1000])
 page.close()
 page=b.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36')
 page.goto('https://alonhadat.com.vn/nha-dat/can-ban/nha-dat/1/ha-noi.html', wait_until='load', timeout=120000); page.wait_for_timeout(3000)
 print('\nalonhadat listing page')
 for x in page.evaluate("""Array.from(document.querySelectorAll('.content-item, .vip, .item')).slice(0,10).map(el=>({text:el.innerText, html:el.outerHTML.slice(0,2000)}))"""):
  print('\nTEXT',x['text'][:1000]); print('HTML',x['html'][:1000])
 b.close()
