from src.analytics.market_analysis import MarketAnalysis


def test_market_summary_handles_empty_data():
    summary = MarketAnalysis().summarize([])
    assert summary['total_listings'] == 0
