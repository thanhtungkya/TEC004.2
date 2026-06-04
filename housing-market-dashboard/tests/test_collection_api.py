from app import app


def test_collection_api_accepts_sources(monkeypatch):
    calls = {}

    def fake_run_all_scrapers(sources=None):
        calls['sources'] = sources
        return {
            'alonhadat': [{'title': 'A', 'district': 'Ba Đình', 'price': 1.2, 'area': 50}],
            'homedy': [],
            'nhadat24h': [],
        }

    monkeypatch.setattr('app.run_all_scrapers', fake_run_all_scrapers)

    client = app.test_client()
    response = client.post('/api/collect', json={
        'sources': ['alonhadat'],
        'keyword': 'test',
        'district': 'Ba Đình',
    })

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['status'] == 'ok'
    assert payload['sources'] == ['alonhadat']
    assert payload['records_saved'] == 1
    assert calls['sources'] == ['alonhadat']
