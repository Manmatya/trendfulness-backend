from fastapi import APIRouter, Depends
from datetime import datetime
import os
import psutil # For system resource monitoring
from cache.redis_client import cache_get
from database.supabase_client import supabase

router = APIRouter(prefix="/health", tags=["System Health"])

@router.get("/")
async def general_health():
    """
    Standard Liveness Check for Railway.
    Returns basic system status and timestamp.
    """
    return {
        "status": "online",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "development"),
        "version": "2.0.0"
    }

@router.get("/detailed")
async def detailed_health():
    """
    Comprehensive health check used by the Admin Dashboard.
    Checks Redis, Supabase connection, and Bot heartbeats.
    """
    # 1. Check Redis via Heartbeat bot data
    bot_heartbeat = await cache_get("system_heartbeat")
    
    # 2. Check Database connectivity
    db_status = "connected"
    try:
        supabase.table("user_profiles").select("count", count="exact").limit(1).execute()
    except Exception:
        db_status = "disconnected"

    # 3. Check System Resources
    process = psutil.Process(os.getpid())
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "cache": "active" if bot_heartbeat else "no_heartbeat",
        "memory_usage_mb": round(process.memory_info().rss / (1024 * 1024), 2),
        "cpu_usage_pct": psutil.cpu_percent(),
        "uptime_report": bot_heartbeat
    }

@router.get("/data-sources")
async def data_source_health():
    """
    Returns the latest health status of FRED, EIA, NOAA, and NSE.
    Data is populated by BOT 1 (data_health_monitor.py).
    """
    try:
        response = supabase.table("data_source_health") \
            .select("*") \
            .order("checked_at", desc=True) \
            .limit(5) \
            .execute()
        return response.data
    except Exception as e:
        return {"error": "Could not retrieve data source health", "details": str(e)}
