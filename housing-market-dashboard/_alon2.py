from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(headless=True); page=b.new_page(user_agent='Mozilla/5.0')
 page.goto('https://alonhadat.com.vn/', wait_until='load', timeout=120000); page.wait_for_timeout(3000)
 xs=page.evaluate("""Array.from(document.querySelectorAll('a[href$=".html"]')).slice(0,20).map(a=>{let c=a; for(let i=0;i<4&&c.parentElement;i++) c=c.parentElement; return {t:a.innerText,h:a.href,html:c.outerHTML.slice(0,1800)}})""")
 for x in xs:
  print('\n---',x['t'],x['h']); print(x['html'])
 b.close()
