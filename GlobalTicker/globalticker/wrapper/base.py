from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import pandas as pd

class BaseProvider(ABC):
    """Abstract base class for data providers."""

    def __init__(self, symbol: str):
        self.symbol = symbol

    @property
    @abstractmethod
    def info(self) -> Dict[str, Any]:
        """Return metadata for the instrument."""
        raise NotImplementedError

    @abstractmethod
    def history(self, start: Optional[str] = None, end: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """Return historical price/NAV with a Date column or index.
        Implementations should return a DataFrame with a DatetimeIndex and a single column named 'Price'.
        """
        raise NotImplementedError