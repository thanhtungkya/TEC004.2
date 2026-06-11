import pandas as pd
import numpy as np


class MarketAnalysis:
    """
    Statistical analysis for the real-estate market.

    Every public method returns plain Python types (dicts / lists of dicts)
    so results can be directly serialised to JSON by Flask's ``jsonify()``.
    """

    # ------------------------------------------------------------------ #
    #  Existing method (preserved)                                        #
    # ------------------------------------------------------------------ #

    def summarize(self, df):
        """Basic market summary: total listings, average price, average area."""
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

    # ------------------------------------------------------------------ #
    #  Price trends by district                                           #
    # ------------------------------------------------------------------ #

    def price_trends_by_district(self, df: pd.DataFrame) -> list:
        """
        Average price per district, sorted from most to least expensive.

        Returns
        -------
        list[dict]
            Each dict: ``{district, avg_price, listing_count}``
        """
        if df.empty or 'district' not in df.columns or 'price' not in df.columns:
            return []

        result = (
            df.groupby('district', as_index=False)
              .agg(
                  avg_price=('price', 'mean'),
                  listing_count=('price', 'size'),
              )
              .sort_values('avg_price', ascending=False)
        )

        # Convert NumPy types to native Python for JSON serialisation
        return self._to_native(result.to_dict('records'))

    # ------------------------------------------------------------------ #
    #  Price-per-m² rankings                                              #
    # ------------------------------------------------------------------ #

    def price_per_m2_rankings(self, df: pd.DataFrame) -> list:
        """
        Average price-per-m² by district, ranked highest first.

        Returns
        -------
        list[dict]
            Each dict: ``{district, avg_price_per_m2, listing_count}``
        """
        if df.empty or 'price_per_m2' not in df.columns:
            return []

        result = (
            df[df['price_per_m2'] > 0]
              .groupby('district', as_index=False)
              .agg(
                  avg_price_per_m2=('price_per_m2', 'mean'),
                  listing_count=('price_per_m2', 'size'),
              )
              .sort_values('avg_price_per_m2', ascending=False)
        )

        return self._to_native(result.to_dict('records'))

    # ------------------------------------------------------------------ #
    #  Property type / source distribution                                #
    # ------------------------------------------------------------------ #

    def property_type_distribution(self, df: pd.DataFrame) -> list:
        """
        Listing count by *source* (acting as a proxy for property type
        since the current schema does not include an explicit type column).

        Returns
        -------
        list[dict]
            Each dict: ``{source, count, percentage}``
        """
        if df.empty or 'source' not in df.columns:
            return []

        counts = df['source'].value_counts()
        total = int(counts.sum())

        result = []
        for source, count in counts.items():
            result.append({
                'source': str(source),
                'count': int(count),
                'percentage': round(float(count / total * 100), 2) if total else 0.0,
            })

        return result

    # ------------------------------------------------------------------ #
    #  Seasonal patterns                                                  #
    # ------------------------------------------------------------------ #

    def seasonal_patterns(self, df: pd.DataFrame) -> list:
        """
        Average price grouped by year-month to reveal seasonal trends.

        Returns
        -------
        list[dict]
            Each dict: ``{year, month, avg_price, listing_count}``
        """
        if df.empty:
            return []

        has_temporal = 'year' in df.columns and 'month' in df.columns
        if not has_temporal:
            return []

        # Drop rows where temporal data is missing
        temporal_df = df.dropna(subset=['year', 'month'])
        if temporal_df.empty:
            return []

        result = (
            temporal_df
              .groupby(['year', 'month'], as_index=False)
              .agg(
                  avg_price=('price', 'mean'),
                  listing_count=('price', 'size'),
              )
              .sort_values(['year', 'month'])
        )

        return self._to_native(result.to_dict('records'))

    # ------------------------------------------------------------------ #
    #  Full report (aggregates all analyses)                              #
    # ------------------------------------------------------------------ #

    def full_report(self, df: pd.DataFrame) -> dict:
        """
        Run every analysis method and bundle the results into a single
        dictionary.

        Returns
        -------
        dict
            Keys: ``summary``, ``price_trends_by_district``,
            ``price_per_m2_rankings``, ``property_type_distribution``,
            ``seasonal_patterns``.
        """
        return {
            'summary': self.summarize(df),
            'price_trends_by_district': self.price_trends_by_district(df),
            'price_per_m2_rankings': self.price_per_m2_rankings(df),
            'property_type_distribution': self.property_type_distribution(df),
            'seasonal_patterns': self.seasonal_patterns(df),
        }

    # ------------------------------------------------------------------ #
    #  Helpers                                                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _to_native(records: list) -> list:
        """Convert NumPy/Pandas scalar types to native Python types."""
        cleaned = []
        for rec in records:
            cleaned.append({
                k: (int(v) if isinstance(v, (np.integer,)) else
                    float(v) if isinstance(v, (np.floating,)) else v)
                for k, v in rec.items()
            })
        return cleaned
