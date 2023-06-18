import asyncio

from broker.kafka import KafkaConsumer, KafkaConsumerService
from db.redis import RedisService, get_redis
from loguru import logger
from message_processing import MessageProcessor
from metrics import mem_health_monitor


async def main():
    asyncio.create_task(mem_health_monitor())
    logger.info('ETL process has started...', extra={'tag': ['etl_app']})

    logger.info('Define consumer and service...', extra={'tag': ['etl_app']})
    consumer = await KafkaConsumer().get_consumer()
    consumer_service: KafkaConsumerService = KafkaConsumerService(consumer)
    logger.info('Success!', extra={'tag': ['etl_app']})

    logger.info('Define cache storage and service...', extra={'tag': ['etl_app']})
    redis = await get_redis()
    cache_service = RedisService(redis)
    logger.info('Success!', extra={'tag': ['etl_app']})

    processor = MessageProcessor(consumer_service, cache_service)
    await processor.do_process()


if __name__ == '__main__':
    asyncio.run(main())
