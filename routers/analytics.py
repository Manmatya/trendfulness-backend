from fastapi import APIRouter
from cache.redis_client import cache_get
import json

router = APIRouter(prefix="/api/analytics", tags=["Admin Dashboard"])

@router.get("/engagement")
async def get_system_engagement():
    """Returns the behavioral data processed by BOT 12."""
    stats = await cache_get("daily_engagement_stats")
    if stats:
        return json.loads(stats)
    return {"message": "No data available yet. Processing..."}
