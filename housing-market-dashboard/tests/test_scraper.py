from unittest.mock import patch
from src.scraper.scraper_manager import run_all_scrapers


@patch('src.scraper.scraper_manager.scrape_alonhadat')
@patch('src.scraper.scraper_manager.scrape_homedy')
@patch('src.scraper.scraper_manager.scrape_nhadat24h')
@patch('src.scraper.scraper_manager.scrape_batdongsan')
@patch('src.scraper.scraper_manager.scrape_mogi')
@patch('src.scraper.scraper_manager.scrape_nhatot')
@patch('src.scraper.scraper_manager.scrape_sosanhnha')
@patch('src.scraper.scraper_manager.scrape_bds123')
@patch('src.scraper.scraper_manager.scrape_nhaongay')
@patch('src.scraper.scraper_manager.scrape_meeyland')
def test_scraper_manager_returns_sources(*mocks):
    for m in mocks:
        m.return_value = []
    data = run_all_scrapers()
    assert set(data) == {
        'alonhadat', 'homedy', 'nhadat24h', 'batdongsan', 'mogi',
        'nhatot', 'sosanhnha', 'bds123', 'nhaongay', 'meeyland'
    }
