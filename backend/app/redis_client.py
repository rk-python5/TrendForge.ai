"""
Redis client setup for caching.
"""

import redis.asyncio as redis
from app.config import settings


async def get_redis_client() -> redis.Redis:
    """Get an async Redis client."""
    return redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True
    )


# Will be initialized on app startup
redis_client: redis.Redis | None = None


async def init_redis():
    """Initialize the Redis connection."""
    global redis_client
    redis_client = await get_redis_client()
    return redis_client


async def close_redis():
    """Close the Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
