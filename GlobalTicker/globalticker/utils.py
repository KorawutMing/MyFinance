from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Optional

def to_datetime_index(df: pd.DataFrame, date_col: Optional[str] = None) -> pd.DataFrame:
    if date_col and date_col in df.columns:
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.set_index(date_col).sort_index()
    elif not isinstance(df.index, pd.DatetimeIndex):
        # attempt to coerce index
        try:
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
        except Exception:
            raise ValueError("DataFrame must have a DatetimeIndex or provide date_col")
    return df


def compute_returns(series: pd.Series, method: str = "pct") -> pd.Series:
    if method == "pct":
        return series.pct_change().dropna()
    if method == "log":
        return np.log(series / series.shift(1)).dropna()
    raise ValueError("method must be 'pct' or 'log'")