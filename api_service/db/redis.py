from redis import asyncio as aioredis

redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    return redis
