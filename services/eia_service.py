import httpx
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
from cache.redis_client import cache_get, cache_set

EIA_API_KEY = os.getenv("EIA_API_KEY")
BASE_URL = "https://api.eia.gov/v2"

# Series IDs for Weekly Petroleum and Natural Gas reports
# 1. Weekly U.S. Field Production of Crude Oil
# 2. Weekly Working Gas in Underground Storage
SERIES = {
    "crude_production": "/petroleum/pri/spt/data/",
    "gas_storage": "/natural-gas/stor/wkly/data/"
}

async def fetch_eia_metrics() -> Dict[str, Any]:
    """
    Fetches energy inventory and production data from EIA.
    Critical for Crude Oil and Natural Gas supply factors.
    """
    cache_key = "macro_eia_data"
    
    cached = await cache_get(cache_key)
    if cached:
        return json.loads(cached)

    results = {}
    async with httpx.AsyncClient(timeout=15.0) as client:
        for label, endpoint in SERIES.items():
            try:
                params = {
                    "api_key": EIA_API_KEY,
                    "frequency": "weekly",
                    "data[0]": "value",
                    "sort[0][column]": "period",
                    "sort[0][direction]": "desc",
                    "length": 2 # Get current and previous for delta
                }
                response = await client.get(f"{BASE_URL}{endpoint}", params=params)
                response.raise_for_status()
                data = response.json().get("response", {}).get("data", [])
                
                if len(data) >= 2:
                    current = float(data[0]["value"])
                    previous = float(data[1]["value"])
                    results[label] = {
                        "value": current,
                        "delta": current - previous,
                        "period": data[0]["period"]
                    }
            except Exception as e:
                print(f"EIA API Error for {label}: {e}")
                results[label] = None

    # Cache for 24 hours (EIA reports are weekly)
    await cache_set(cache_key, json.dumps(results), 86400)
    return results

async def get_energy_score(commodity: str) -> float:
    """
    Scoring logic: 
    Crude: Inventory Draw (Negative Delta) = Bullish (Higher Score)
    Natural Gas: Inventory Build < Seasonal Avg = Bullish
    """
    data = await fetch_eia_metrics()
    
    if commodity.upper() == "CRUDE OIL":
        metric = data.get("crude_production")
        if not metric: return 50.0
        # If production is falling, it's bullish
        return 70.0 if metric["delta"] < 0 else 40.0
        
    if commodity.upper() == "NAT GAS":
        metric = data.get("gas_storage")
        if not metric: return 50.0
        # Inventory build (positive delta) is seasonally bearish
        return 35.0 if metric["delta"] > 0 else 65.0

    return 50.0
