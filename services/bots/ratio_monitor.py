import json
from typing import Dict, Any
from services.pair_signals import calculate_pair_ratios
from cache.redis_client import cache_set

async def run():
    """
    BOT 9: Inter-Commodity Ratio Watchdog.
    Tracks GSR (Gold-Silver Ratio) and others for extreme divergences.
    """
    print("BOT 9: Checking commodity ratios for divergences...")
    try:
        ratios = await calculate_pair_ratios()
        
        # Identify extreme moves (e.g., GSR > 90 or < 70)
        for pair, data in ratios.items():
            if abs(data.get("z_score", 0)) > 2.0:
                print(f"ALERT: Extreme divergence in {pair} (Z-Score: {data['z_score']})")
        
        await cache_set("latest_ratios", json.dumps(ratios), 3600)
    except Exception as e:
        print(f"BOT 9 Error: {e}")
