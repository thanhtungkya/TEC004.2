from app import app
from src.analytics.market_analysis import MarketAnalysis


def test_market_summary_handles_empty_data():
    summary = MarketAnalysis().summarize([])
    assert summary['total_listings'] == 0


def test_root_redirects_to_dashboard():
    response = app.test_client().get("/")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
