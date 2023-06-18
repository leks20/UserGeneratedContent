import json
from abc import ABC, abstractmethod
from typing import Any

import backoff
from redis import asyncio as aioredis
from redis.exceptions import ConnectionError, RedisError


class AsyncKeyValueService(ABC):
    @abstractmethod
    async def start(self):
        ...

    @abstractmethod
    async def put_data(self, key: str, data: Any) -> Any | None:
        ...

    @abstractmethod
    async def get_data(self, key: str) -> list[Any] | None:  # noqa: WPS463
        ...


class RedisService(AsyncKeyValueService):  # noqa: WPS214
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

    async def get_data(self, key):
        data = await self.redis.get(key)
        if not data:
            return None
        return json.loads(data)

    @backoff.on_exception(backoff.expo, RedisError, max_time=10)
    async def add_to_sorted_set(self, sorted_set: str, key: str, data: float = 0):
        await self.redis.zadd(sorted_set, {key: data})

    @backoff.on_exception(backoff.expo, RedisError, max_time=10)
    async def remove_from_sorted_set(self, sorted_set: str, *args):
        await self.redis.zrem(sorted_set, *args)

    @backoff.on_exception(backoff.expo, RedisError, max_time=10)
    async def get_value_sorted_set(self, sorted_set: str, key: str):
        return await self.redis.zscore(sorted_set, key)

    @backoff.on_exception(backoff.expo, RedisError, max_time=10)
    async def get_sorted_list(self, sorted_set: str, start: int, end: int):
        return await self.redis.zrange(sorted_set, start, end, withscores=True)
