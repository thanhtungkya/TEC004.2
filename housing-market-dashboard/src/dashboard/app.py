import streamlit as st

from src.database.create_tables import create_tables
from src.database.property_repository import PropertyRepository
from src.processing.transform_data import transform_records
from src.analytics.market_analysis import MarketAnalysis


def main():
    create_tables()

    st.set_page_config(page_title="Housing Market Dashboard", layout="wide")
    st.title("Housing Market Dashboard")
    st.caption("Starter dashboard for scraping, cleaning, and analyzing housing listings.")

    repo = PropertyRepository()
    records = repo.fetch_all()
    df = transform_records([dict(row) for row in records])

    if df.empty:
        st.info("No property data is available yet. Run the scraper or seed the database first.")
        return

    summary = MarketAnalysis().summarize(df)
    col1, col2, col3 = st.columns(3)
    col1.metric("Listings", summary['total_listings'])
    col2.metric("Average Price", f"{summary['avg_price']:.0f}")
    col3.metric("Average Area (m2)", f"{summary['avg_area']:.1f}")

    st.dataframe(df.head(20), use_container_width=True)
