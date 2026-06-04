import pandas as pd


class MarketAnalysis:
    def summarize(self, df):
        frame = df if isinstance(df, pd.DataFrame) else pd.DataFrame(df)

        if frame.empty:
            return {
                'total_listings': 0,
                'avg_price': 0.0,
                'avg_area': 0.0,
            }

        return {
            'total_listings': int(len(frame)),
            'avg_price': float(frame['price'].mean()) if 'price' in frame.columns else 0.0,
            'avg_area': float(frame['area'].mean()) if 'area' in frame.columns else 0.0,
        }
