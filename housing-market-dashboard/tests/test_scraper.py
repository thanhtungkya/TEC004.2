from src.scraper.scraper_manager import run_all_scrapers


def test_scraper_manager_returns_sources():
    data = run_all_scrapers()
    assert set(data) == {'alonhadat', 'homedy', 'nhadat24h'}
