from functools import lru_cache

import backoff
from aiokafka import AIOKafkaConsumer
from broker.base import BaseConsumer, BaseConsumerService
from kafka.errors import KafkaConnectionError
from settings import settings


class KafkaConsumer(BaseConsumer):
    @lru_cache
    async def get_consumer(self):
        return AIOKafkaConsumer(
            settings.kafka_topic,
            bootstrap_servers=[settings.bootstrap_ulr],
            auto_offset_reset='latest',
            group_id='redis_group',
            enable_auto_commit=False,
        )


class KafkaConsumerService(BaseConsumerService):
    def __init__(self, consumer: AIOKafkaConsumer):
        self.consumer = consumer

    @backoff.on_exception(backoff.expo, KafkaConnectionError, max_time=10)
    async def start(self):
        await self.consumer.start()

    @backoff.on_exception(backoff.expo, KafkaConnectionError, max_time=10)
    async def close(self):
        await self.consumer.stop()

    @backoff.on_exception(backoff.expo, KafkaConnectionError, max_time=10)
    async def get_records(self):
        async for msg in self.consumer:
            yield msg

    @backoff.on_exception(backoff.expo, KafkaConnectionError, max_time=10)
    async def commit_changes(self):
        await self.consumer.commit()
