import uvicorn
from fastapi import FastAPI, HTTPException, Query
from urllib.parse import unquote
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging
import os
import sys

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.append(root_path)

from GlobalTicker.globalticker.ticker import GlobalTicker

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GlobalTicker API")

# Cache for GlobalTicker instances
ticker_cache: Dict[str, GlobalTicker] = {}

def get_or_create_ticker(symbol: str, currency: str = "THB") -> GlobalTicker:
    """Get ticker from cache or create new one with special handling for FX"""
    clean_symbol = unquote(symbol).upper()
    
    # Check if the symbol is a currency pair (e.g., USDTHB)
    # Yahoo Finance uses the format 'USDTHB=X' for exchange rates
    if len(clean_symbol) == 6 and clean_symbol.isalpha() and not clean_symbol.endswith(".BK"):
        # If the user requested USDTHB, we use the Yahoo FX symbol
        yf_symbol = f"{clean_symbol}=X"
        logger.info(f"Detected FX pair. Mapping {clean_symbol} to {yf_symbol}")
    else:
        yf_symbol = clean_symbol

    cache_key = f"{yf_symbol}_{currency}"
    
    if cache_key not in ticker_cache:
        logger.info(f"Creating new ticker for {yf_symbol} with currency {currency}")
        # Note: For USDTHB=X, the base currency is usually implied by the pair
        ticker_cache[cache_key] = GlobalTicker(yf_symbol, currency=currency)
    else:
        logger.info(f"Using cached ticker for {yf_symbol}")
    
    return ticker_cache[cache_key]

@app.get("/market-data/{symbol}")
def get_fund_data(
    symbol: str,
    currency: str = Query(default="THB", description="Currency for price conversion")
):
    """Get latest price for a symbol (including FX pairs like USDTHB)"""
    try:
        ticker = get_or_create_ticker(symbol, currency)
        
        end_date = datetime.today()
        start_date = end_date - timedelta(days=7) # Small window for latest price
        
        df = ticker.history(
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d")
        )
        
        if df is None or df.empty:
            raise ValueError(f"No data returned for {symbol}")
        
        latest = df.iloc[-1]
        latest_date = df.index[-1]
        
        return {
            "symbol": symbol.upper(),
            "price": float(latest["Price"]),
            "date": latest_date.strftime("%Y-%m-%d"),
            "currency": currency,
            "is_fx": "=X" in ticker.symbol
        }
    except Exception as e:
        logger.error(f"Error for {symbol}: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/market-data/{symbol}/history")
def get_fund_history(
    symbol: str,
    days: int = Query(default=365, description="Number of days of history"),
    currency: str = Query(default="THB", description="Currency for price conversion")
):
    """Get historical data for a symbol"""
    clean_symbol = unquote(symbol)
    
    try:
        # Get or create ticker
        ticker = get_or_create_ticker(clean_symbol, currency)
        
        # Fetch history
        end_date = datetime.today()
        start_date = end_date - timedelta(days=days)
        
        logger.info(f"Fetching {days} days of history for {clean_symbol}")
        
        df = ticker.history(
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d")
        )
        
        if df is None or df.empty:
            raise ValueError(f"No data returned for {clean_symbol}")
        
        logger.info(f"Got {len(df)} rows for {clean_symbol}")
        
        # Convert to list of records
        records = []
        for date, row in df.iterrows():
            records.append({
                "date": date.strftime("%Y-%m-%d") if hasattr(date, 'strftime') else str(date),
                "price": float(row["Price"])
            })
        
        return {
            "symbol": clean_symbol,
            "currency": currency,
            "data_points": len(records),
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "history": records
        }
        
    except Exception as e:
        logger.error(f"Error for {clean_symbol}: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=f"Error fetching data for {clean_symbol}: {str(e)}"
        )

@app.post("/cache/clear")
def clear_cache():
    """Clear the ticker cache"""
    global ticker_cache
    count = len(ticker_cache)
    ticker_cache.clear()
    return {
        "message": f"Cache cleared, removed {count} tickers"
    }

@app.get("/cache/status")
def cache_status():
    """Get cache status"""
    return {
        "cached_tickers": list(ticker_cache.keys()),
        "count": len(ticker_cache)
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/test-notebook-symbols")
def test_notebook_symbols():
    """Test all symbols from your notebook"""
    symbols = [
        "SCBDBOND(A)",
        "NVDA",
        "AMD",
        "INTC",
        "UVAN.BK",
        "SCBGOLDH"
    ]
    
    results = {}
    currency = "THB"
    
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    
    for symbol in symbols:
        try:
            ticker = get_or_create_ticker(symbol, currency)
            df = ticker.history(
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d")
            )
            
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                latest_date = df.index[-1]
                results[symbol] = {
                    "success": True,
                    "price": float(latest["Price"]),
                    "date": str(latest_date),
                    "data_points": len(df)
                }
            else:
                results[symbol] = {
                    "success": False,
                    "error": "No data returned"
                }
        except Exception as e:
            results[symbol] = {
                "success": False,
                "error": str(e)
            }
    
    return results

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)