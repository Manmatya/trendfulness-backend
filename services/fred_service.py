import httpx
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from cache.redis_client import cache_get, cache_set

# FRED Series IDs
# DGS10: 10-Year Treasury Constant Maturity Rate
# T10YIE: 10-Year Breakeven Inflation Rate
SERIES_IDS = {
    "yield_10y": "DGS10",
    "inflation_10y": "T10YIE"
}

FRED_API_KEY = os.getenv("FRED_API_KEY")
BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

async def fetch_macro_indicators() -> Dict[str, float]:
    """
    Fetches real rates and yields from FRED.
    Calculates Real Rate = Nominal Yield - Breakeven Inflation.
    """
    cache_key = "macro_fred_data"
    
    # 1. Try Cache (Macro data only needs to update once every few hours)
    cached = await cache_get(cache_key)
    if cached:
        return json.loads(cached)

    results = {}
    async with httpx.AsyncClient(timeout=10.0) as client:
        for label, series_id in SERIES_IDS.items():
            try:
                params = {
                    "series_id": series_id,
                    "api_key": FRED_API_KEY,
                    "file_type": "json",
                    "sort_order": "desc",
                    "limit": 1
                }
                response = await client.get(BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
                
                if "observations" in data and len(data["observations"]) > 0:
                    val = data["observations"][0]["value"]
                    # FRED sometimes returns "." for holidays/weekends
                    results[label] = float(val) if val != "." else None
            except Exception as e:
                print(f"FRED API Error for {series_id}: {e}")
                results[label] = None

    # 2. Calculate Derived Real Rate
    # If both values exist, calculate; otherwise, use fallback logic (BOT 4)
    if results.get("yield_10y") and results.get("inflation_10y"):
        real_rate = results["yield_10y"] - results["inflation_10y"]
        results["real_rate_10y"] = round(real_rate, 4)
    else:
        # Fallback to a neutral value if data is missing
        results["real_rate_10y"] = 1.50 

    # 3. Cache for 4 hours (Macro doesn't move as fast as price)
    await cache_set(cache_key, json.dumps(results), 14400)
    
    return results

async def get_macro_score() -> float:
    """
    Translates macro data into a 0-100 score for the Scoring Engine.
    Higher Real Rates = Bearish for Gold (Lower Score).
    """
    data = await fetch_macro_indicators()
    real_rate = data.get("real_rate_10y", 1.5)
    
    # Simple Scoring Logic:
    # Real Rate > 2.0% is very restrictive (Bearish Score: 20-40)
    # Real Rate < 0.0% is very stimulative (Bullish Score: 70-90)
    if real_rate > 2.0: return 30.0
    if real_rate < 0.0: return 85.0
    
    # Linear interpolation between 0 and 2%
    # 0% -> 80, 2% -> 40
    score = 80 - (real_rate * 20)
    return round(score, 2)
