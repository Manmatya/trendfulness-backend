import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional
from cache.redis_client import cache_get, cache_set
import json

SYMBOLS = {
    "GC=F": "GOLD", "SI=F": "SILVER", "CL=F": "CRUDE OIL",
    "BZ=F": "BRENT CRUDE", "NG=F": "NAT GAS", "DX-Y.NYB": "DXY", "VIX": "VIX"
}

async def fetch_all_prices() -> Dict[str, Any]:
    cache_key = "prices:all"
    cached = await cache_get(cache_key)
    if cached: return json.loads(cached)

    try:
        data = yf.download(list(SYMBOLS.keys()), period="1d", interval="1m", progress=False)
        results = {}
        for sym, label in SYMBOLS.items():
            price = data['Close'][sym].dropna().iloc[-1]
            change = ((price - data['Open'][sym].iloc[0]) / data['Open'][sym].iloc[0]) * 100
            results[sym] = {"label": label, "price": round(price, 2), "change": round(change, 2)}
        
        await cache_set(cache_key, json.dumps(results), 30)
        return results
    except Exception:
        return {}

async def get_historical_ohlcv(symbol: str, interval: str, bars: int = 60) -> Optional[pd.DataFrame]:
    mapping = {"3hr": "90m", "daily": "1d", "weekly": "1wk"}
    try:
        df = yf.download(symbol, period="1mo" if interval=="3hr" else "1y", 
                         interval=mapping.get(interval, "1d"), progress=False)
        return df.tail(bars)
    except Exception:
        return None
