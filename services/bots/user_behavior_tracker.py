import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from database.supabase_client import supabase
from cache.redis_client import cache_set

class UserBehaviorTrackerBot:
    """
    BOT 12: Analytics & Engagement Intelligence.
    Processes raw event logs to identify trending commodities and feature gaps.
    """

    @classmethod
    async def run(cls):
        """
        Scheduled task: Aggregates 'user_events' to find trends over the last 24h.
        """
        print("BOT 12: Analyzing user behavior patterns...")
        
        one_day_ago = (datetime.utcnow() - timedelta(days=1)).isoformat()

        try:
            # 1. Fetch raw events from Supabase
            response = supabase.table("user_events") \
                .select("commodity, event_type, time_spent_seconds") \
                .gt("created_at", one_day_ago) \
                .execute()

            events = response.data
            if not events:
                print("BOT 12: No event data found for the last 24h.")
                return

            # 2. Process Aggregations
            stats = cls._calculate_engagement(events)

            # 3. Store insights in Redis for the Admin Dashboard
            await cache_set("daily_engagement_stats", json.dumps(stats), 86400)
            
            # 4. Persistence: Log summary to long-term analytics table
            supabase.table("weekly_analytics_reports").insert({
                "week_start": datetime.utcnow().date().isoformat(),
                "top_commodities": stats["top_commodities"],
                "tab_engagement": stats["event_breakdown"],
                "created_at": datetime.utcnow().isoformat()
            }).execute()

            print("BOT 12: Behavioral analysis complete and stored.")

        except Exception as e:
            print(f"BOT 12 Error: {e}")

    @staticmethod
    def _calculate_engagement(events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates top viewed commodities and feature usage ratios."""
        comm_counts = {}
        event_types = {}
        total_seconds = 0

        for e in events:
            # Track most viewed commodities
            comm = e.get("commodity", "General")
            comm_counts[comm] = comm_counts.get(comm, 0) + 1
            
            # Track which features (event_types) are popular
            etype = e.get("event_type", "unknown")
            event_types[etype] = event_types.get(etype, 0) + 1
            
            # Sum total session time
            total_seconds += e.get("time_spent_seconds", 0)

        # Sort commodities by popularity
        sorted_comms = dict(sorted(comm_counts.items(), key=lambda item: item[1], reverse=True))

        return {
            "top_commodities": sorted_comms,
            "event_breakdown": event_types,
            "avg_session_time_mins": round((total_seconds / len(events)) / 60, 2) if events else 0
        }

async def run():
    """Bot entry point for scheduler."""
    await UserBehaviorTrackerBot.run()
