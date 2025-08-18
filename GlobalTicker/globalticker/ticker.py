from typing import Optional, Dict, Any
import pandas as pd
from .wrapper.yahoo_wrapper import YahooProvider
from .wrapper.thai_nav_wrapper import ThaiNAVProvider
from .wrapper.base import BaseProvider
from .exceptions import ProviderNotFound
from .utils import compute_returns

class GlobalTicker:
    """Unified interface exposing a yfinance-like API with optional currency conversion."""

    def __init__(self, symbol: str, provider: Optional[str] = None, currency: str = "native"):
        """
        :param symbol: Ticker symbol
        :param provider: "yahoo" or "thai_nav" (if None → try both)
        :param currency: "native", "THB" or "USD"
        """
        self.symbol = symbol
        self.currency = currency.upper()

        # Explicit provider requested
        if provider == "yahoo":
            self.provider: BaseProvider = YahooProvider(symbol)
            self.provider_name = "yahoo"
        elif provider == "thai_nav":
            self.provider = ThaiNAVProvider(symbol)
            self.provider_name = "thai_nav"
        elif provider is None:
            # Try ThaiNAV first
            try:
                prov = ThaiNAVProvider(symbol)
                if prov.info:   # confirm it works
                    self.provider = prov
                    self.provider_name = "thai_nav"
                else:
                    raise ValueError("ThaiNAV has no info")
            except Exception:
                # fallback to Yahoo
                try:
                    self.provider = YahooProvider(symbol)
                    self.provider_name = "yahoo"
                except Exception:
                    raise ProviderNotFound(f"No provider worked for {symbol}")
        else:
            raise ProviderNotFound(f"Unknown provider: {provider}")

    @property
    def info(self) -> Dict[str, Any]:
        info = self.provider.info.copy()
        info["currency"] = self.currency
        return info

    def history(self, start: Optional[str] = None, end: Optional[str] = None, **kwargs) -> pd.DataFrame:
        df = self.provider.history(start=start, end=end, **kwargs).copy()
        df.index = pd.to_datetime(df.index).tz_localize(None)

        native_ccy = self.provider.currency().upper()
        target_ccy = self.currency.upper()

        if target_ccy == "NATIVE" or target_ccy == native_ccy:
            return df

        if {native_ccy, target_ccy} != {"THB", "USD"}:
            raise ValueError(f"Unsupported currency conversion: {native_ccy} -> {target_ccy}")

        fx = YahooProvider("THB=X").history(start=start, end=end)["Price"].copy()
        fx.index = pd.to_datetime(fx.index).tz_localize(None)

        df = df.reindex(fx.index).ffill()

        if native_ccy == "THB" and target_ccy == "USD":
            df["Price"] = df["Price"] / fx
        elif native_ccy == "USD" and target_ccy == "THB":
            df["Price"] = df["Price"] * fx

        return df

    def returns(self, start: Optional[str] = None, end: Optional[str] = None, method: str = "pct") -> pd.Series:
        hist = self.history(start=start, end=end)
        if hist is None or hist.empty:
            return hist
        return compute_returns(hist["Price"], method=method)
