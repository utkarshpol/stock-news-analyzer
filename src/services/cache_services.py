# src/services/cache_service.py
import json
import os
from typing import Any, Optional
# CRITICAL: Import the asynchronous client to prevent thread block type-mismatches
from redis.asyncio import Redis 

class CacheService:
    """
    Asynchronous utility abstraction handler for managing structural 
    data object payloads inside the shared Redis container instance.
    """
    _instance: Optional[Redis] = None

    @classmethod
    def get_client(cls) -> Redis:
        """Singleton connection pattern factory ensuring minimal connection pool strain."""
        if cls._instance is None:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            # Using decode_responses=True converts bytes to strings automatically
            cls._instance = Redis.from_url(redis_url, decode_responses=True)
        return cls._instance

    @classmethod 
    async def get(cls, key: str) -> Optional[Any]:
        """Fetch an item out of Redis memory asynchronously and parse its JSON schema."""
        try:
            client = cls.get_client()
            # Added 'await' here! This resolves the ResponseT / Awaitable type error.
            data = await client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"⚠️ App Cache Lookup Failure for Key [{key}]: {str(e)}")
        return None

    @classmethod
    async def set(cls, key: str, value: Any, ttl_seconds: int = 900) -> bool:
        """Commit an object schema to Redis memory bounded by an explicit TTL window."""
        try:
            client = cls.get_client()
            serialized_data = json.dumps(value)
            # Added 'await' here to cleanly resolve the async execution loop
            await client.setex(key, ttl_seconds, serialized_data)
            return True
        except Exception as e:
            print(f"⚠️ App Cache Write Failure for Key [{key}]: {str(e)}")
            return False