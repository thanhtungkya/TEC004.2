import pandas as pd


def transform_records(records):
    df = pd.DataFrame(records)
    if df.empty:
        return df

    df["price"] = pd.to_numeric(df.get("price", 0), errors="coerce").fillna(0)
    df["area"] = pd.to_numeric(df.get("area", 0), errors="coerce").fillna(0)
    df["district"] = df.get("district", "Unknown").fillna("Unknown")
    return df
