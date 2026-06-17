import sys
import os

# Ensure the app context works
sys.path.append(os.path.abspath('.'))

from src.scraper.alonhadat_scraper import scrape_alonhadat
from src.scraper.batdongsan_scraper import scrape_batdongsan
from src.scraper.bds123_scraper import scrape_bds123
from src.scraper.homedy_scraper import scrape_homedy
from src.scraper.meeyland_scraper import scrape_meeyland
from src.scraper.mogi_scraper import scrape_mogi
from src.scraper.nhadat24h_scraper import scrape_nhadat24h
from src.scraper.nhadatviet123_scraper import scrape_nhadatviet123
from src.scraper.nhaongay_scraper import scrape_nhaongay
from src.scraper.nhatot_scraper import scrape_nhatot
from src.scraper.sosanhnha_scraper import scrape_sosanhnha

def test_scrapers():
    scrapers = {
        'alonhadat': scrape_alonhadat,
        'batdongsan': scrape_batdongsan,
        'bds123': scrape_bds123,
        'homedy': scrape_homedy,
        'meeyland': scrape_meeyland,
        'mogi': scrape_mogi,
        'nhadat24h': scrape_nhadat24h,
        '123nhadatviet': scrape_nhadatviet123,
        'nhaongay': scrape_nhaongay,
        'nhatot': scrape_nhatot,
        'sosanhnha': scrape_sosanhnha
    }
    
    with open('test_scraper_results.txt', 'w', encoding='utf-8') as f:
        for name, func in scrapers.items():
            try:
                print(f"Testing {name}...")
                records = func()
                f.write(f"{name}: {len(records)} records\n")
                if records:
                    f.write(f"Sample: {records[0]}\n")
            except Exception as e:
                f.write(f"{name}: Failed with {e}\n")
            f.write("-" * 40 + "\n")

if __name__ == "__main__":
    test_scrapers()
