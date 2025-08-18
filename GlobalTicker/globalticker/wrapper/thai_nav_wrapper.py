from __future__ import annotations
from typing import Any, Dict, Optional
import pandas as pd
import pythainav as nav
from .base import BaseProvider

class ThaiNAVProvider(BaseProvider):
    """Provider using pythainav for Thai mutual funds."""

    def __init__(self, symbol: str):
        super().__init__(symbol)
        # Preload entire history once
        df = nav.get_all(symbol, asDataFrame=True)
        if df is None or len(df) == 0:
            raise ValueError(f"Fund not found or no data: {symbol}")
        df = df.copy()
        df["updated"] = pd.to_datetime(df["updated"], errors="coerce")
        df = df.dropna(subset=["updated"]).sort_values("updated").reset_index(drop=True)
        self._df = df

    @property
    def info(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "type": "thai_mutual_fund",
            "start_date": self._df["updated"].min().strftime("%Y-%m-%d"),
            "last_date": self._df["updated"].max().strftime("%Y-%m-%d"),
            "last_value": float(self._df["value"].iloc[-1]),
        }
    
    def currency(self) -> str:
        return "THB"

    def history(self, start: Optional[str] = None, end: Optional[str] = None, **kwargs) -> pd.DataFrame:
        df = self._df
        if start is not None:
            df = df[df["updated"] >= pd.to_datetime(start)]
        if end is not None:
            df = df[df["updated"] <= pd.to_datetime(end)]
        out = df[["updated", "value"]].copy()
        out = out.rename(columns={"updated": "Date", "value": "Price"})
        out = out.set_index("Date").sort_index()
        return out
