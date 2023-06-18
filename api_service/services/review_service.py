import uuid
from functools import lru_cache

import backoff
from bson import ObjectId
from fastapi import Depends
from motor import motor_asyncio
from pymongo.errors import ServerSelectionTimeoutError

from db.mongo import get_mongo
from models.reviews import ReviewDTO
from services.rating_service import RatingService, get_rating_service


class ReviewAlreadyExistsError(BaseException):
    pass


class ReviewNotFoundError(BaseException):
    pass


class UserAlreadyLikedError(BaseException):
    pass


class UserAlreadyDislikedError(BaseException):
    pass


class ReviewService:
    COLLECTION_NAME = 'reviews'

    def __init__(
        self,
        mongo_db: motor_asyncio.AsyncIOMotorDatabase,
        rating_service: RatingService,
    ):
        self.db = mongo_db
        self.collection = self.db.get_collection(self.COLLECTION_NAME)
        self.rating_service = rating_service

    async def add_review(self, review: ReviewDTO):
        existing_review = await self.collection.find_one(
            {'user_id': review.user_id, 'text': review.text}
        )
        if existing_review is not None:
            raise ReviewAlreadyExistsError()

        average_rating = await self.rating_service.get_movie_rating(
            str(review.movie_id)
        )
        review.rating = average_rating.rating

        result = await self.collection.insert_one(review.dict())
        return result

    @backoff.on_exception(backoff.expo, ServerSelectionTimeoutError, max_time=10)
    async def add_like_to_review(self, review_id: str, user_id: uuid.UUID):
        review = await self.collection.find_one({'_id': ObjectId(review_id)})

        if review is None:
            raise ReviewNotFoundError()
        if user_id in review.get('users_liked', []):
            raise UserAlreadyLikedError()

        result = await self.collection.update_one(
            {'_id': ObjectId(review_id)},
            {'$inc': {'like_count': 1}, '$push': {'users_liked': user_id}},
        )
        return result

    @backoff.on_exception(backoff.expo, ServerSelectionTimeoutError, max_time=10)
    async def add_dislike_to_review(self, review_id: str, user_id: uuid.UUID):
        review = await self.collection.find_one({'_id': ObjectId(review_id)})

        if review is None:
            raise ReviewNotFoundError()

        if user_id in review.get('users_disliked', []):
            raise UserAlreadyDislikedError()
        result = await self.collection.update_one(
            {'_id': ObjectId(review_id)},
            {
                '$inc': {'dislike_count': 1},
                '$push': {'users_disliked': user_id},
            },
        )
        return result

    @backoff.on_exception(backoff.expo, ServerSelectionTimeoutError, max_time=10)
    async def get_reviews(self, sort_by: str | None):
        if sort_by is None:
            result = self.collection.find()
        else:
            result = self.collection.find().sort(sort_by)
        reviews = []

        async for review in result:
            reviews.append(ReviewDTO(**review))
        return reviews


@lru_cache()
def get_review_service(
    mongo=Depends(get_mongo), rating_service=Depends(get_rating_service)
):
    return ReviewService(mongo, rating_service)
