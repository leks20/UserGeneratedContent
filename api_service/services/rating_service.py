import uuid
from functools import lru_cache

import backoff
from bson import ObjectId
from fastapi import Depends
from motor import motor_asyncio
from pydantic import UUID4, BaseModel
from pymongo.errors import ServerSelectionTimeoutError
from redis import asyncio as aioredis

from db.mongo import get_mongo
from db.redis import get_redis
from models.ratings import RatingDeleteDTO, RatingDTO, RatingMongoDTO
from services.redis_service import RedisService


class RatingAlreadyExists(BaseException):
    ...


class RatingNotFoundError(BaseException):
    ...


class SameRatingError(BaseException):
    ...


class MovieRating(BaseModel):
    movie_id: UUID4
    rating: float = 0.0


class RatingRedisService(RedisService):
    rating_sorted_set = 'movies_by_rating'

    async def add_to_score_table(self, movie_id, rating):
        await self.add_to_sorted_set(self.rating_sorted_set, str(movie_id), rating)

    async def remove_from_score_table(self, movie_id):
        await self.remove_from_sorted_set(self.rating_sorted_set, str(movie_id))

    async def get_from_score_table(self, movie_id):
        return await self.get_value_sorted_set(self.rating_sorted_set, str(movie_id))

    async def get_score_table(self, start, end):
        return await self.get_sorted_list(self.rating_sorted_set, start, end)


@lru_cache
def get_rating_redis_service(redis: aioredis.Redis = Depends(get_redis)):
    return RatingRedisService(redis)


class RatingService:
    COLLECTION_NAME = 'ratings'

    def __init__(
        self,
        mongo_connector: motor_asyncio.AsyncIOMotorClient,
        redis_service: RatingRedisService,
    ):
        self.db = mongo_connector['UGC']
        self.collection = self.db[self.COLLECTION_NAME]
        self.redis = redis_service

    async def calc_average(self, movie_id: uuid.UUID):
        pipeline = [
            {'$match': {'movie_id': movie_id}},
            {'$group': {'_id': None, 'average_rating': {'$avg': '$rating'}}},
        ]

        result = await self.collection.aggregate(pipeline).to_list(1) or None
        if result:
            return result[0]['average_rating']
        return None

    async def update_and_cache_rating(self, movie_id: uuid.UUID):
        rating_average = await self.calc_average(movie_id)

        if rating_average is None:
            return await self.redis.remove_from_score_table(movie_id)

        return await self.redis.add_to_score_table(movie_id, rating_average)

    @backoff.on_exception(backoff.expo, ServerSelectionTimeoutError, max_time=10)
    async def add_rating(self, rating_info: RatingDTO):
        if await self.collection.find_one(
            {'movie_id': rating_info.movie_id, 'user_id': rating_info.user_id}
        ):
            raise RatingAlreadyExists()
        result = await self.collection.insert_one(rating_info.dict())

        await self.update_and_cache_rating(rating_info.movie_id)

        return result

    @backoff.on_exception(backoff.expo, ServerSelectionTimeoutError, max_time=10)
    async def update_rating(self, rating_info: RatingDTO):
        rating = await self.collection.find_one(
            {'movie_id': rating_info.movie_id, 'user_id': rating_info.user_id}
        )
        if rating is None:
            raise RatingNotFoundError()

        rating_dto = RatingMongoDTO(**rating)

        if rating_dto.rating == rating_info.rating:
            raise SameRatingError()

        updated_rating = await self.collection.update_one(
            {'_id': ObjectId(rating_dto.id)}, {'$set': rating_info.dict()}
        )

        await self.update_and_cache_rating(rating_info.movie_id)

        return updated_rating

    @backoff.on_exception(backoff.expo, ServerSelectionTimeoutError, max_time=10)
    async def remove_rating(self, remove_rating_info: RatingDeleteDTO):
        result = await self.collection.find_one_and_delete(remove_rating_info.dict())

        if result is None:
            raise RatingNotFoundError()

        await self.update_and_cache_rating(remove_rating_info.movie_id)

        return result

    async def get_rating_table(self, page, limit):
        range_end = page * limit
        range_start = range_end - limit
        table_values = await self.redis.get_score_table(range_start, range_end - 1)

        return [
            MovieRating(movie_id=table[0], rating=table[1]) for table in table_values
        ]

    async def get_movie_rating(self, key: str):
        rating = await self.redis.get_from_score_table(key)
        if rating is None:
            rating = 0.0
        return MovieRating(movie_id=key, rating=rating)


@lru_cache
def get_rating_service(
    mongo=Depends(get_mongo),
    rating_redis_service=Depends(get_rating_redis_service),
):
    return RatingService(mongo, rating_redis_service)
