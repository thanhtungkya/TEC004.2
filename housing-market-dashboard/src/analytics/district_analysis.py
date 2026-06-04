import pandas as pd


class DistrictAnalysis:
    def top_districts(self, df: pd.DataFrame, limit: int = 5):
        if df.empty:
            return []

        return (
            df.groupby('district', as_index=False)
              .agg(listings=('title', 'size'), avg_price=('price', 'mean'))
              .sort_values('listings', ascending=False)
              .head(limit)
              .to_dict('records')
        )
