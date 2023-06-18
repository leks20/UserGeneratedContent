import json
from typing import Any

import backoff
from db.base import AsyncKeyValueService
from redis import asyncio as aioredis
from redis.exceptions import ConnectionError, RedisError
from settings import settings

redis: aioredis.Redis = aioredis.from_url(settings.redis_url)


async def get_redis() -> aioredis.Redis:
    return redis


class RedisService(AsyncKeyValueService):
    def __init__(self, redis_connector: aioredis.Redis):
        self.redis = redis_connector

    @backoff.on_exception(backoff.expo, ConnectionError, max_time=10)
    async def start(self):
        await self.redis.ping()

    @backoff.on_exception(backoff.expo, RedisError, max_time=10)
    async def put_data(self, key: str, data: Any):
        if not data:
            return
        await self.redis.set(key, json.dumps(data))

    @backoff.on_exception(backoff.expo, RedisError, max_time=10)
    async def get_data(self, key):
        data = await self.redis.get(key)
        if not data:
            return None
        return json.loads(data.decode('utf-8'))
