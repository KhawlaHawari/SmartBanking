from __future__ import annotations

import pandas as pd


def clean_dataset_headers(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    clean_df = df.copy()
    clean_df.columns = clean_df.iloc[0]
    clean_df = clean_df.iloc[1:].reset_index(drop=True)
    clean_df.columns = [str(col).strip().lower().replace(" ", "_") for col in clean_df.columns]
    return clean_df
