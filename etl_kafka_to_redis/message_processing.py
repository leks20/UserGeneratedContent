from datetime import datetime

import backoff
from broker.base import BaseConsumerService
from db.redis import AsyncKeyValueService
from kafka.errors import KafkaError
from loguru import logger
from pydantic import BaseModel


class MovieDTO(BaseModel):
    progress: float
    user_id: str
    movie_id: str
    event_time: datetime


class MessageProcessor:
    def __init__(
        self,
        consumer_service: BaseConsumerService,
        storage_service: AsyncKeyValueService,
    ):
        self.consumer_service = consumer_service
        self.storage_service = storage_service

    async def check_services(self):
        logger.info('Checking connection for services...', extra={'tag': ['etl_app']})
        await self.consumer_service.start()
        await self.storage_service.start()

    @backoff.on_exception(backoff.expo, KafkaError, max_time=5)
    async def do_process(self):
        await self.check_services()

        logger.info('Ready to process messages.', extra={'tag': ['etl_app']})
        try:
            async for msg in self.consumer_service.get_records():
                dto = MovieDTO.parse_raw(msg.value)

                await self.storage_service.put_data(msg.key, dto.progress)
                await self.consumer_service.commit_changes()
                logger.debug(
                    'Message has been processed. Raw: %s DTO: %s',
                    msg,
                    dto,
                    extra={'tag': ['etl_app']},
                )
        finally:
            await self.consumer_service.close()
