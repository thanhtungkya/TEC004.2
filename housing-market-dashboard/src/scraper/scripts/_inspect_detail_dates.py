from playwright.sync_api import sync_playwright
urls=[
'https://alonhadat.com.vn/-truc-10m5-hiem-gan-song-han-3-tang-kien-co-vua-o-vua-kinh-doanh-cuc-dinh-18745728.html',
'https://homedy.com/ban-nha-rieng-quan-nam-tu-liem-ha-noi/3-tang-tai-le-quang-dao-gia-hiem-es3209208',
'https://nhadat24h.net/ban-chung-cu-quan-go-vap/ch-pham-van-dong-vao-o-lien-cat-lo-2ty-full-noi-that-so-hong-rieng-ID4373291'
]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True)
 for url in urls:
  page=b.new_page(user_agent='Mozilla/5.0')
  page.goto(url, wait_until='load', timeout=120000); page.wait_for_timeout(3000)
  print('\nURL', url, 'TITLE', page.title())
  body=page.locator('body').inner_text(timeout=5000)
  for line in body.splitlines():
   if any(k in line.lower() for k in ['ngày đăng','đăng ngày','hôm nay','hôm qua','cập nhật','date','tháng','trước']):
    print(line[:300])
  page.close()
 b.close()
