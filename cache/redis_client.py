import redis.asyncio as redis
import os
import json
from typing import Optional, Any
from datetime import timedelta

# Railway auto-injects REDIS_URL when the Redis plugin is added.
# Local development fallback: redis://localhost:6379
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

class RedisClient:
    """
    Asynchronous Redis client wrapper for Trendfulness.
    Handles caching for prices, AI narratives, and bot heartbeats.
    """
    def __init__(self):
        try:
            self.client = redis.from_url(
                REDIS_URL, 
                encoding="utf-8", 
                decode_responses=True,
                socket_timeout=5.0
            )
        except Exception as e:
            print(f"CRITICAL: Failed to connect to Redis at {REDIS_URL}: {e}")
            self.client = None

    async def get(self, key: str) -> Optional[str]:
        """Retrieve a value from cache."""
        if not self.client: return None
        try:
            return await self.client.get(key)
        except Exception as e:
            print(f"Redis GET Error ({key}): {e}")
            return None

    async def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """
        Store a value in cache with an expiration time.
        Converts dicts/lists to JSON strings automatically.
        """
        if not self.client: return False
        try:
            # Handle complex types
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            await self.client.setex(key, ttl_seconds, value)
            return True
        except Exception as e:
            print(f"Redis SET Error ({key}): {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Remove a key from cache."""
        if not self.client: return False
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            print(f"Redis DELETE Error ({key}): {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        if not self.client: return False
        try:
            return await self.client.exists(key) > 0
        except Exception:
            return False

# Initialize a single global instance for the application
cache = RedisClient()

# Functional aliases for easier importing
async def cache_get(key: str) -> Optional[str]:
    return await cache.get(key)

async def cache_set(key: str, value: Any, ttl: int = 3600) -> bool:
    return await cache.set(key, value, ttl)

async def cache_delete(key: str) -> bool:
    return await cache.delete(key)
