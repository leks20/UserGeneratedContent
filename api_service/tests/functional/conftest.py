import asyncio
from typing import Iterator

import pytest
from fastapi import FastAPI
from motor import motor_asyncio
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from starlette.testclient import TestClient

from conf.config import mongo_settings, settings
from services.bookmark_service import BookmarkService
from services.review_service import ReviewService
from tests.functional.utils import (
    get_bookmark_from_file,
    get_fake_bookmarks,
    get_fake_reviews,
    get_review_from_file,
    get_user_token,
)
from webapp.main import create_app

API_VERSION = 'v0'


@pytest.fixture(scope='module')
def app() -> FastAPI:
    app = create_app()
    yield app


@pytest.fixture(scope='session', autouse=True)
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='module')
def client(app):
    with TestClient(app=app, headers={'Authorization': get_user_token()}) as client:
        yield client


@pytest.fixture(scope='module')
async def client_mongo_db(app):
    client = motor_asyncio.AsyncIOMotorClient(
        mongo_settings.connect_ulr, uuidRepresentation='standard'
    )
    await client.admin.command('ping')
    yield client[mongo_settings.db_name]

    client.close()


@pytest.fixture()
async def bookmark_collection(
    client_mongo_db: AsyncIOMotorDatabase,
) -> Iterator[AsyncIOMotorCollection]:
    collection = client_mongo_db.get_collection(BookmarkService.COLLECTION_NAME)
    yield collection
    await collection.delete_many({})


@pytest.fixture(scope='module')
def app_url(app):
    return f'http://{settings.bind_ip}:{settings.bind_port}/api/{API_VERSION}'


@pytest.fixture(scope='module')
def bookmark_ulr(app_url):
    return f'{app_url}/bookmarks/'


@pytest.fixture()
def bookmark_ulr_delete(bookmark_ulr, bookmark_data):
    movie_id = bookmark_data['movie_id']
    return bookmark_ulr + movie_id + '/'


@pytest.fixture()
def bookmark_data():
    return get_bookmark_from_file()


@pytest.fixture()
async def prepare_bookmarks(bookmark_collection):
    load_data = [data.dict() for data in get_fake_bookmarks()]

    await bookmark_collection.insert_many(load_data)
    return bookmark_collection


@pytest.fixture()
async def review_collection(
    client_mongo_db: AsyncIOMotorDatabase,
) -> Iterator[AsyncIOMotorCollection]:
    collection = client_mongo_db.get_collection(ReviewService.COLLECTION_NAME)
    yield collection
    await collection.delete_many({})


@pytest.fixture()
def review_data():
    return get_review_from_file()


@pytest.fixture()
async def prepare_reviews(review_collection):
    load_data = [data.dict() for data in get_fake_reviews()]
    await review_collection.insert_many(load_data)
    return review_collection


@pytest.fixture(scope='module')
def review_url(app_url):
    return f'{app_url}/reviews/'
