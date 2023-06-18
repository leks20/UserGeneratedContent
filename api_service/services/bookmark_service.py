import uuid
from datetime import datetime
from functools import lru_cache

import backoff
from fastapi import Depends
from motor import motor_asyncio
from pydantic.types import UUID4
from pymongo.errors import ServerSelectionTimeoutError

from db.mongo import get_mongo
from models.base import MovieModel
from models.bookmarks import BookmarksResponseModel


class BookmarkAlreadyExists(BaseException):
    pass


class BookmarkNotFound(BaseException):
    pass


class Bookmark(MovieModel):
    user_id: UUID4


class BookmarkCreateDTO(Bookmark):
    created_at: datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class BookmarkService:
    COLLECTION_NAME = 'bookmarks'

    def __init__(self, mongo_db: motor_asyncio.AsyncIOMotorDatabase):
        self.db = mongo_db
        self.collection = self.db.get_collection(self.COLLECTION_NAME)

    @backoff.on_exception(backoff.expo, ServerSelectionTimeoutError, max_time=10)
    async def add_bookmark(self, bookmark: BookmarkCreateDTO):
        bookmark_dict = bookmark.dict()
        request = bookmark_dict.copy()
        request.pop('created_at')
        if await self.collection.find_one(request):
            raise BookmarkAlreadyExists()
        result = await self.collection.insert_one(bookmark.dict())
        return result

    @backoff.on_exception(backoff.expo, ServerSelectionTimeoutError, max_time=10)
    async def remove_bookmark(self, bookmark: Bookmark):
        result = await self.collection.find_one_and_delete(bookmark.dict())
        if result is None:
            raise BookmarkNotFound()
        return result

    @backoff.on_exception(backoff.expo, ServerSelectionTimeoutError, max_time=10)
    async def get_user_bookmarks(self, user_id: uuid.UUID):
        result = self.collection.find(
            {'user_id': user_id},
            {'_id': 0, 'user_id': 0},
        ).sort('created_at', -1)
        bookmarks = []
        async for bookmark in result:
            bookmarks.append(BookmarksResponseModel(**bookmark))
        return bookmarks


@lru_cache()
def get_bookmark_service(mongo=Depends(get_mongo)):
    return BookmarkService(mongo)
