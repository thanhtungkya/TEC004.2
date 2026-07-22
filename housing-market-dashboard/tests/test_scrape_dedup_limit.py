from src.scraper.selenium_scraper import collect_cards_from_sources, normalize_listing_url, SCRAPE_LINK_LIMIT
from src.scraper import scraper_manager


def test_collect_cards_skips_existing_then_moves_to_next_category(monkeypatch):
    calls = []

    def fake_render(url, selector, card_selector=None):
        calls.append(url)
        if url == 'cat-1':
            return [
                {'url': 'https://site.test/a?utm=old', 'title': 'old'},
                {'url': 'https://site.test/b', 'title': 'new-b'},
            ]
        return [{'url': 'https://site.test/c', 'title': 'new-c'}]

    monkeypatch.setattr('src.scraper.selenium_scraper.render_listing_cards', fake_render)
    cards = collect_cards_from_sources(
        'site', ['cat-1', 'cat-2'], 'a[href]', existing_urls={'https://site.test/a'}, limit=2
    )

    assert calls == ['cat-1', 'cat-2']
    assert [normalize_listing_url(card['url']) for card in cards] == ['https://site.test/b', 'https://site.test/c']


def test_scraper_manager_passes_existing_urls_and_1000_limit(monkeypatch):
    captured = {}

    class FakeRepo:
        def fetch_urls(self):
            return ['https://site.test/existing?x=1']

    def fake_scraper(**kwargs):
        captured.update(kwargs)
        return [{'url': 'https://site.test/new'}]

    monkeypatch.setattr(scraper_manager, 'PropertyRepository', lambda: FakeRepo())
    monkeypatch.setitem(scraper_manager.run_all_scrapers.__globals__['scrapers'] if False else {}, 'noop', fake_scraper)
    monkeypatch.setattr(scraper_manager, 'scrape_alonhadat', fake_scraper)

    result = scraper_manager.run_all_scrapers(['alonhadat'])

    assert result == {'alonhadat': [{'url': 'https://site.test/new'}]}
    assert captured['link_limit'] == SCRAPE_LINK_LIMIT == 1000
    assert 'https://site.test/existing' in captured['existing_urls']
