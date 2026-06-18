import os
import glob

scraper_dir = r"c:\Users\Duy\Documents\GitHub\TEC004.2\housing-market-dashboard\src\scraper"

# 1. Update selenium_scraper.py regexes
sel_file = os.path.join(scraper_dir, "selenium_scraper.py")
with open(sel_file, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(r"(?!\s*(?:/|trên)\s*m)", r"(?!\s*(?:/|trên)\s*(?:m|th|tháng))")
content = content.replace(r"(?!\s*(?:\/|trên)\s*m)", r"(?!\s*(?:\/|trên)\s*(?:m|th|tháng))")

with open(sel_file, "w", encoding="utf-8") as f:
    f.write(content)

# 2. Update all other scrapers
for f_name in glob.glob(os.path.join(scraper_dir, "*_scraper.py")):
    if "selenium_scraper" in f_name or "manager" in f_name:
        continue
    with open(f_name, "r", encoding="utf-8") as f:
        code = f.read()

    # Replace the standard pattern
    code = code.replace(
        "price_text = normalise_price_text(item.get('price_text') or cleaned)",
        "price_text = normalise_price_text(item.get('price_text')) or normalise_price_text(cleaned)"
    )

    # Special handling for nhadat24h
    if "nhadat24h" in f_name:
        code = code.replace(
            "raw_price = item.get('price_text') or cleaned\n        price_text = normalise_price_text(raw_price)",
            "price_text = normalise_price_text(item.get('price_text')) or normalise_price_text(cleaned)"
        )

    with open(f_name, "w", encoding="utf-8") as f:
        f.write(code)

print("Patching complete.")
