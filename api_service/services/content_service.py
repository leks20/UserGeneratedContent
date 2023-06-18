from functools import lru_cache
from uuid import UUID

from fastapi import Depends
from redis import RedisError, asyncio as aioredis

from db.redis import get_redis
from services.redis_service import AsyncKeyValueService, RedisService
from webapp.logging import logger


class MovieContentService:
    def __init__(self, storage_service: AsyncKeyValueService):
        self.storage_service = storage_service

    @staticmethod
    def form_key(user_id, movie_id):
        return f'{str(user_id)}:{str(movie_id)}'

    async def get_movie_watching_progress(self, user_id: UUID, movie_id: UUID):
        try:
            return await self.storage_service.get_data(self.form_key(user_id, movie_id))
        except RedisError as e:
            logger.warning(
                f'Error occurs while getting movie progress '
                f'from storage. Error: {str(e)}. Return zero.',
                extra={'tag': ['fast_api_app']},
            )
            return 0


@lru_cache
def get_movie_content_svc(redis: aioredis.Redis = Depends(get_redis)):
    return MovieContentService(RedisService(redis))
