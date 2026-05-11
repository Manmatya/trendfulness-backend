import nsepython
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from cache.redis_client import cache_get, cache_set

# Exactly the MCX symbols required for Trendfulness
MCX_SYMBOLS = ["GOLDM", "SILVERM", "CRUDEOIL"]

async def fetch_mcx_prices() -> Dict[str, Any]:
    """
    Fetch live MCX futures prices using nsepython.
    Includes 30-second caching to prevent rate-limiting and improve speed.
    """
    cache_key = "live_prices_mcx"
    
    # 1. Try Cache First
    cached_data = await cache_get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    results = {}
    
    # 2. Fetch Data with Error Handling
    for symbol in MCX_SYMBOLS:
        try:
            # Wrap synchronous nsepython call to prevent blocking the event loop
            loop = asyncio.get_event_loop()
            # nse_quote_ltp returns the Last Traded Price
            ltp = await loop.run_in_executor(None, nsepython.nse_quote_ltp, symbol)
            
            if ltp:
                results[f"{symbol}.MCX"] = {
                    "label": f"{symbol} MCX",
                    "price": float(ltp),
                    "currency": "INR",
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            # BOT 1 & 4 logic: Log error but don't crash the entire loop
            print(f"Error fetching MCX data for {symbol}: {e}")
            continue

    # 3. Handle Graceful Degradation
    if not results:
        # If all fetches fail, return an empty dict or trigger BOT 4 logic
        return {"warning": "MCX data currently unavailable", "data": {}}

    # 4. Set Cache for 30 Seconds
    await cache_set(cache_key, json.dumps(results), 30)
    
    return results

async def get_mcx_ohlcv(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves full quote data for deeper technical analysis.
    """
    try:
        loop = asyncio.get_event_loop()
        full_quote = await loop.run_in_executor(None, nsepython.nse_quote_meta, symbol)
        return full_quote
    except Exception as e:
        print(f"Error fetching MCX metadata for {symbol}: {e}")
        return None
