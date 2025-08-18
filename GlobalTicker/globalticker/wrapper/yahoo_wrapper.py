from __future__ import annotations
from typing import Any, Dict, Optional
import pandas as pd
import yfinance as yf
from .base import BaseProvider

class YahooProvider(BaseProvider):
    """Provider using yfinance for global stocks/ETFs."""

    def __init__(self, symbol: str):
        super().__init__(symbol)
        self._ticker = yf.Ticker(symbol)

    @property
    def info(self) -> Dict[str, Any]:
        # yfinance returns dict; keep as-is
        return self._ticker.info
    
    def currency(self) -> str:
        return self.info.get("currency", "").upper()

    def history(self, start: Optional[str] = None, end: Optional[str] = None, **kwargs) -> pd.DataFrame:
        df = self._ticker.history(start=start, end=end, **kwargs)
        df.index = pd.to_datetime(df.index).tz_localize(None)
        if df.empty:
            return df
        # standardize to a single 'Price' column (Close)
        out = pd.DataFrame(index=df.index.copy())
        out["Price"] = df["Close"].astype(float)
        return out