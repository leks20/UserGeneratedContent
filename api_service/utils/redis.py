from redis import asyncio as aioredis

from conf.config import redis_settings
from db import redis


async def connect_to_redis():
    redis.redis = aioredis.Redis(
        host=redis_settings.host,
        port=redis_settings.port,
        decode_responses=True,
    )


async def stop_redis():
    await redis.redis.close()
