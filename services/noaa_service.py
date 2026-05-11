import httpx
import os
import json
from typing import Dict, Any
from datetime import datetime
from cache.redis_client import cache_get, cache_set

NOAA_API_KEY = os.getenv("NOAA_API_KEY")
# Using GFS (Global Forecast System) data via NOAA's climate endpoints
BASE_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"

async def fetch_weather_impact() -> Dict[str, Any]:
    """
    Fetches temperature anomalies for key US natural gas consumption hubs.
    Used to predict Natural Gas demand (Heating Degree Days / Cooling Degree Days).
    """
    cache_key = "macro_noaa_data"
    
    cached = await cache_get(cache_key)
    if cached:
        return json.loads(cached)

    # Simplified logic: Checking if temperatures are significantly above/below normal
    results = {"impact": "NEUTRAL", "value": 50}
    
    try:
        # Note: In production, this would query specific stations in the US Northeast/Midwest
        # For the prototype, we use a structured fallback/placeholder for the scoring logic
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"token": NOAA_API_KEY}
            # Placeholder for actual station-based query logic
            # response = await client.get(BASE_URL, headers=headers, params=...)
            
            # Logic: If Winter + Colder than avg -> Bullish Nat Gas
            # Logic: If Summer + Hotter than avg -> Bullish Nat Gas (AC Demand)
            results = {"impact": "BULLISH", "value": 75} # Example result
            
    except Exception as e:
        print(f"NOAA API Error: {e}")

    await cache_set(cache_key, json.dumps(results), 43200) # Cache 12 hours
    return results
