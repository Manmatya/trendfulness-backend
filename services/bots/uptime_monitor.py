import httpx
import asyncio
import os
from datetime import datetime
from typing import Dict, Any
from cache.redis_client import cache_set

class UptimeMonitorBot:
    """
    BOT 8: Critical System Health & Latency Monitor.
    Pings the platform's own endpoints and external dependencies to ensure 99.9% availability.
    """

    def __init__(self):
        self.targets = {
            "self_api": "http://localhost:8000/health",
            "supabase": os.getenv("SUPABASE_URL", ""),
            "gemini_api": "https://generativelanguage.googleapis.com/v1beta/models",
            "fred_api": "https://api.stlouisfed.org/fred/series",
            "eia_api": "https://api.eia.gov/v2"
        }

    async def check_target(self, name: str, url: str) -> Dict[str, Any]:
        """Pings a specific URL and measures response time."""
        if not url:
            return {"status": "CONFIG_ERROR", "latency_ms": 0}

        start_time = datetime.now()
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Use a simple GET or HEAD request
                response = await client.get(url)
                latency = (datetime.now() - start_time).total_seconds() * 1000
                
                status = "UP" if response.status_code < 400 else "DEGRADED"
                return {
                    "status": status,
                    "latency_ms": round(latency, 2),
                    "code": response.status_code
                }
        except Exception as e:
            return {
                "status": "DOWN",
                "latency_ms": 0,
                "error": str(e)
            }

    async def run_audit(self):
        """Executes a full sweep of all critical infrastructure."""
        report = {}
        for name, url in self.targets.items():
            report[name] = await self.check_target(name, url)

        # Log to console for Railway logs
        print(f"BOT 8 [Uptime]: {datetime.utcnow()} - Audit Complete.")
        
        # Store latest heartbeat in Redis for the Admin Dashboard
        await cache_set("system_heartbeat", str(report), 600) # 10 min TTL

        # Alerting Logic (BOT 4 Trigger)
        if report["self_api"]["status"] == "DOWN":
            print("CRITICAL ALERT: Backend API is unresponsive!")
            # Integration with Twilio/Email could be added here

async def run():
    """Bot entry point for APScheduler."""
    monitor = UptimeMonitorBot()
    await monitor.run_audit()
