import os
import re

scraper_dir = 'c:/Users/Duy/Documents/GitHub/TEC004.2/housing-market-dashboard/src/scraper'

updates = {
    'batdongsan': ("'a.js__product-link-for-product-id', '.js__card'"),
    'bds123': ("'a.bg-white.text-black'"),
    'meeyland': ("'a.flex', '.card-article'"),
    'nhadat24h': ("'.pn1 a', '.pn1'"),
    'nhadatviet123': ("'.ct_title a', '.item'"),
    'nhaongay': ("'.card-title a', '.card'"),
    'nhatot': ("'li a[href*=\".htm\"]'"),
    'sosanhnha': ("'a.js__card-title'")
}

for name, selector_args in updates.items():
    filepath = os.path.join(scraper_dir, f"{name}_scraper.py")
    if not os.path.exists(filepath):
        continue
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # The existing render_listing_cards(URL, '...', '...') call might be multi-line
    # We will regex replace the inside of render_listing_cards(...)
    # Because there are different formats, we can use a simpler approach:
    # Just regex replace the whole render_listing_cards call
    
    # regex: render_listing_cards\(\s*[A-Z0-9_]+_URL\s*,[\s\S]*?\)
    var_name = name.upper() + "_URL"
    if name == 'nhadatviet123':
        var_name = 'NHADATVIET123_URL'
        
    new_call = f"render_listing_cards(\n        {var_name},\n        {selector_args}\n    )"
    
    content = re.sub(r"render_listing_cards\(\s*[A-Z0-9_]+_URL\s*,[^)]+\)", new_call, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Updated selectors. Running test_scrapers.py...")
os.system("python test_scrapers.py")
