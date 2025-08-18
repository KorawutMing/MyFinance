from __future__ import annotations
from typing import Iterable, Optional, Dict
import pandas as pd
from .ticker import GlobalTicker


def download(symbols: Iterable[str], start: Optional[str] = None, end: Optional[str] = None, provider: Optional[str] = None, **kwargs) -> pd.DataFrame:
    """Download multiple symbols into a single DataFrame with aligned Date index.

    Returns a DataFrame with one column per symbol, each holding unified 'Price' series (Close for equities, NAV for funds).
    """
    if isinstance(symbols, (str,)):
        symbols = [symbols]

    data: Dict[str, pd.Series] = {}
    for sym in symbols:
        t = GlobalTicker(sym, provider=provider)
        hist = t.history(start=start, end=end, **kwargs)
        if hist is None or hist.empty:
            continue
        series = hist["Price"].rename(sym)
        data[sym] = series

    if not data:
        return pd.DataFrame()

    df = pd.concat(data.values(), axis=1)
    df.index.name = "Date"
    return df