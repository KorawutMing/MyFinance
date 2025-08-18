# GlobalTicker 📈

**GlobalTicker** provides a unified, yfinance-like interface for multiple markets:

- **Yahoo Finance** for global stocks/ETFs (via `yfinance`)
- **Thai mutual funds** for NAV (via `pythainav`)

## Installation
```bash
pip install -e .
```

## Quick Start
```python
from globalticker import GlobalTicker, download

# Yahoo / global equity
nvda = GlobalTicker("NVDA")
print(nvda.info)
print(nvda.history(start="2024-01-01").tail())  # Close mapped to Price

# Thai mutual fund (AIMC code)
scb = GlobalTicker("SCBDBOND(A)")
print(scb.info)
print(scb.history(start="2024-08-01").tail())   # NAV mapped to Price

# Multi-download into aligned frame
df = download(["NVDA", "SCBDBOND(A)", "AAPL"], start="2024-01-01")
print(df.tail())
```

## Design
- Each provider implements `BaseProvider` and returns a DataFrame with a single `Price` column indexed by `Date` (DatetimeIndex).
- `GlobalTicker.history()` simply proxies to the provider while preserving the standard schema.
- `download()` aggregates multiple `Price` series into a single wide DataFrame.

## Roadmap
- Add SET equities/ETFs provider (`settrade-v2`).
- Caching layer (local CSV/Parquet) to reduce network calls.
- Plot helpers and risk metrics (vol, drawdown, Sharpe).

## License
- MIT