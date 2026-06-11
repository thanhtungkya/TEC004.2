import pandas as pd
import numpy as np


class DistrictAnalysis:
    """
    Per-district statistical analysis for real-estate listings.

    All public methods return JSON-friendly Python types.
    """

    # ------------------------------------------------------------------ #
    #  Existing method (preserved)                                        #
    # ------------------------------------------------------------------ #

    def top_districts(self, df: pd.DataFrame, limit: int = 5):
        """Return the districts with the most listings."""
        if df.empty:
            return []

        return (
            df.groupby('district', as_index=False)
              .agg(listings=('title', 'size'), avg_price=('price', 'mean'))
              .sort_values('listings', ascending=False)
              .head(limit)
              .to_dict('records')
        )

    # ------------------------------------------------------------------ #
    #  Price statistics per district                                      #
    # ------------------------------------------------------------------ #

    def price_statistics(self, df: pd.DataFrame) -> list:
        """
        Descriptive statistics of **price** for every district.

        Uses NumPy for core calculations (mean, median, std, min, max).

        Returns
        -------
        list[dict]
            Each dict: ``{district, count, mean, median, min, max, std}``
        """
        if df.empty or 'district' not in df.columns or 'price' not in df.columns:
            return []

        results = []
        for district, group in df.groupby('district'):
            prices = group['price'].dropna().to_numpy(dtype=np.float64)
            if len(prices) == 0:
                continue
            results.append({
                'district': str(district),
                'count': int(len(prices)),
                'mean': round(float(np.mean(prices)), 2),
                'median': round(float(np.median(prices)), 2),
                'min': round(float(np.min(prices)), 2),
                'max': round(float(np.max(prices)), 2),
                'std': round(float(np.std(prices, ddof=1)), 2) if len(prices) > 1 else 0.0,
            })

        # Sort by mean price descending
        results.sort(key=lambda x: x['mean'], reverse=True)
        return results

    # ------------------------------------------------------------------ #
    #  Area statistics per district                                      #
    # ------------------------------------------------------------------ #

    def area_statistics(self, df: pd.DataFrame) -> list:
        """
        Descriptive statistics of **area** for every district.

        Uses NumPy for core calculations.

        Returns
        -------
        list[dict]
            Each dict: ``{district, count, mean, median, min, max}``
        """
        if df.empty or 'district' not in df.columns or 'area' not in df.columns:
            return []

        results = []
        for district, group in df.groupby('district'):
            areas = group['area'].dropna().to_numpy(dtype=np.float64)
            # Only consider positive areas
            areas = areas[areas > 0]
            if len(areas) == 0:
                continue
            results.append({
                'district': str(district),
                'count': int(len(areas)),
                'mean': round(float(np.mean(areas)), 2),
                'median': round(float(np.median(areas)), 2),
                'min': round(float(np.min(areas)), 2),
                'max': round(float(np.max(areas)), 2),
            })

        # Sort by mean area descending
        results.sort(key=lambda x: x['mean'], reverse=True)
        return results
