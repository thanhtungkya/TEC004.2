import pandas as pd
import numpy as np

from src.processing.clean_price import clean_price
from src.processing.clean_area import clean_area


class DataCleaner:
    """
    Pandas-based data cleaning pipeline for real-estate listings.

    Pipeline steps (executed in order by ``clean()``):
        1. Convert raw records to a DataFrame
        2. Clean price & area columns (Vietnamese string → numeric)
        3. Handle missing values (median imputation for numerics)
        4. Remove duplicate listings
        5. Detect outliers using the IQR method (flagged, not removed)
        6. Normalize prices to *triệu VND*
        7. Compute derived columns (``price_per_m2``, ``month``, ``year``)
    """

    # Columns considered when identifying duplicate listings
    DUPLICATE_SUBSET = ['title', 'district', 'price', 'area']

    # Multiplier used by IQR outlier detection (1.5 = standard)
    IQR_MULTIPLIER = 1.5

    # ------------------------------------------------------------------ #
    #  Public API                                                         #
    # ------------------------------------------------------------------ #

    def clean(self, records) -> pd.DataFrame:
        """Run the full cleaning pipeline and return a tidy DataFrame."""
        df = self._to_dataframe(records)
        if df.empty:
            return df

        df = self._clean_price_column(df)
        df = self._clean_area_column(df)
        df = self._handle_missing_values(df)
        df = self._remove_duplicates(df)
        df = self._detect_outliers(df)
        df = self._normalize_prices(df)
        df = self._compute_derived_columns(df)
        return df

    # ------------------------------------------------------------------ #
    #  Step 1 – DataFrame conversion                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _to_dataframe(records) -> pd.DataFrame:
        """Accept a list-of-dicts, an existing DataFrame, or sqlite3.Row objects."""
        if isinstance(records, pd.DataFrame):
            return records.copy()
        return pd.DataFrame(records)

    # ------------------------------------------------------------------ #
    #  Step 2 – Price & area parsing                                      #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _clean_price_column(df: pd.DataFrame) -> pd.DataFrame:
        """Apply ``clean_price()`` to the *price* column."""
        if 'price' in df.columns:
            df['price'] = df['price'].apply(clean_price)
        return df

    @staticmethod
    def _clean_area_column(df: pd.DataFrame) -> pd.DataFrame:
        """Apply ``clean_area()`` to the *area* column."""
        if 'area' in df.columns:
            df['area'] = df['area'].apply(clean_area)
        return df

    # ------------------------------------------------------------------ #
    #  Step 3 – Missing value handling                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
        """
        Fill missing values:
        - Numeric columns (``price``, ``area``): fill with column **median**.
        - Text columns (``district``, ``title``, ``source``): fill with
          ``"Unknown"``.
        """
        # Numeric columns — median imputation
        for col in ('price', 'area'):
            if col in df.columns:
                median_val = df[col].median()
                # If the entire column is NaN the median is NaN; fall back to 0
                fill_val = median_val if pd.notna(median_val) else 0.0
                df[col] = df[col].fillna(fill_val)

        # Text columns.  Pandas/SQLite data can contain real NaN values or the
        # literal string "nan"; neither should be rendered as user-facing text.
        for col in ('district', 'address', 'title', 'source', 'url'):
            if col in df.columns:
                df[col] = df[col].replace({np.nan: None, 'nan': None, 'NaN': None, 'None': None, 'null': None})
                if col == 'url':
                    df[col] = df[col].fillna('')
                else:
                    df[col] = df[col].fillna('Unknown')

        return df

    # ------------------------------------------------------------------ #
    #  Step 4 – Duplicate removal                                         #
    # ------------------------------------------------------------------ #

    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Drop exact-duplicate rows based on key listing columns."""
        subset = [c for c in self.DUPLICATE_SUBSET if c in df.columns]
        if subset:
            df = df.drop_duplicates(subset=subset, keep='first').reset_index(drop=True)
        return df

    # ------------------------------------------------------------------ #
    #  Step 5 – Outlier detection (IQR method)                            #
    # ------------------------------------------------------------------ #

    def _detect_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Flag outliers using the **IQR method** (NumPy).

        For each numeric column (``price``, ``area``) a boolean column
        ``is_outlier_<col>`` is added.  A combined ``is_outlier`` column
        is ``True`` when *any* single-column flag is ``True``.

        Outlier rows are **flagged, not removed**, so downstream
        consumers can decide how to handle them.
        """
        outlier_flags = []

        for col in ('price', 'area'):
            if col not in df.columns:
                continue

            values = df[col].to_numpy(dtype=np.float64, na_value=np.nan)
            valid = values[~np.isnan(values)]

            if len(valid) < 4:
                # Not enough data for meaningful IQR
                df[f'is_outlier_{col}'] = False
                outlier_flags.append(f'is_outlier_{col}')
                continue

            q1 = np.percentile(valid, 25)
            q3 = np.percentile(valid, 75)
            iqr = q3 - q1
            lower_bound = q1 - self.IQR_MULTIPLIER * iqr
            upper_bound = q3 + self.IQR_MULTIPLIER * iqr

            df[f'is_outlier_{col}'] = (df[col] < lower_bound) | (df[col] > upper_bound)
            outlier_flags.append(f'is_outlier_{col}')

        # Combined flag
        if outlier_flags:
            df['is_outlier'] = df[outlier_flags].any(axis=1)
        else:
            df['is_outlier'] = False

        return df

    # ------------------------------------------------------------------ #
    #  Step 6 – Price normalisation                                       #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _normalize_prices(df: pd.DataFrame) -> pd.DataFrame:
        """
        Ensure all prices are expressed in **triệu VND**.

        ``clean_price()`` already converts to triệu, so this step
        simply ensures the column is a clean float64.
        """
        if 'price' in df.columns:
            df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0.0)
        return df

    # ------------------------------------------------------------------ #
    #  Step 7 – Derived columns                                           #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _compute_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add analytical columns:
        - ``price_per_m2``: price ÷ area (0 when area is 0)
        - ``month``, ``year``: extracted from ``created_at``
        """
        # Price per m²
        if 'price' in df.columns and 'area' in df.columns:
            df['price_per_m2'] = np.where(
                df['area'] > 0,
                df['price'] / df['area'],
                0.0,
            )

        # Temporal features
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
            df['month'] = df['created_at'].dt.month
            df['year'] = df['created_at'].dt.year

        return df


# ====================================================================== #
#  Backward-compatible wrapper                                            #
# ====================================================================== #

def transform_records(records):
    """
    Legacy helper kept for backward compatibility with existing callers
    (e.g. ``app.py``).  Delegates to :class:`DataCleaner`.
    """
    return DataCleaner().clean(records)
