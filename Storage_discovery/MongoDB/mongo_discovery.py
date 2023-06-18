import asyncio
import random
import time
import uuid
from datetime import datetime
from functools import wraps

import faker
from motor.motor_asyncio import AsyncIOMotorClient


def async_timer(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = await func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f'Function {func.__name__} took {elapsed_time:.4f} seconds to execute')
        return result

    return wrapper


async def create_conn():
    return AsyncIOMotorClient('mongodb://mongos1:27017')


@async_timer
async def create_collections(client):
    db = client.testDB
    collections = ['Likes', 'Reviews', 'Bookmarks']

    for collection_name in collections:
        collection = await db.create_collection(collection_name)

        await collection.create_index([('_id', 'hashed')])

    await asyncio.sleep(1)


@async_timer
async def enable_sharding(client):
    admin_db = client.admin
    await admin_db.command('enableSharding', 'testDB')

    await admin_db.command('shardCollection', 'testDB.Likes', key={'_id': 'hashed'})
    await admin_db.command('shardCollection', 'testDB.Reviews', key={'_id': 'hashed'})
    await admin_db.command('shardCollection', 'testDB.Bookmarks', key={'_id': 'hashed'})


@async_timer
async def insert_data(client):
    fake = faker.Faker()

    unique_users = [str(uuid.uuid4()) for _ in range(100_000)]
    unique_movies = [str(uuid.uuid4()) for _ in range(50_000)]

    users_list = unique_users * 10
    movies_list = unique_movies * 20

    random.shuffle(users_list)
    random.shuffle(movies_list)

    likes_records = [
        {
            'user_id': users_list[i],
            'movie_id': movies_list[i],
            'rating': random.randint(0, 10),  # noqa: S311
        }
        for i in range(1000_000)
    ]

    await client.testDB.Likes.insert_many(likes_records)

    reviews_records = [
        {
            'text': fake.text(),
            'publication_date': datetime.combine(
                fake.date_between(start_date='-1y', end_date='today'),
                datetime.min.time(),
            ),
            'author': fake.name(),
            'movie_id': movies_list[i],
        }
        for i in range(1000_000)
    ]

    await client.testDB.Reviews.insert_many(reviews_records)

    bookmarks_records = [
        {'user_id': users_list[i], 'movie_id': movies_list[i]} for i in range(1000_000)
    ]

    await client.testDB.Bookmarks.insert_many(bookmarks_records)


@async_timer
async def read_data(client):
    await client.testDB.Likes.find({}, {'_id': 1}).to_list(length=1000_000)
    await client.testDB.Reviews.find({}, {'_id': 1}).to_list(length=1000_000)
    await client.testDB.Bookmarks.find({}, {'_id': 1}).to_list(length=1000_000)


@async_timer
async def average_user_rating(client, movie_id):
    pipeline = [
        {'$match': {'movie_id': movie_id}},
        {'$group': {'_id': None, 'avgRating': {'$avg': '$rating'}}},
    ]
    avg_rating = await client.testDB.Likes.aggregate(pipeline).to_list(length=1)
    print(f'Average rating for movie {movie_id} is {avg_rating[0]["avgRating"]}')


@async_timer
async def get_user_likes(client, user_id):
    user_likes = await client.testDB.Likes.find(
        {'user_id': user_id, 'rating': {'$gt': 8}}
    ).to_list(length=1000_000)
    return user_likes


@async_timer
async def get_movie_likes(client, movie_id):
    movie_likes = await client.testDB.Likes.count_documents(
        {'movie_id': movie_id, 'rating': {'$gt': 8}}
    )
    print(f'Movie {movie_id} has {movie_likes} likes.')
    return movie_likes


@async_timer
async def get_movie_dislikes(client, movie_id):
    movie_dislikes = await client.testDB.Likes.count_documents(
        {'movie_id': movie_id, 'rating': {'$lt': 2}}
    )
    print(f'Movie {movie_id} has {movie_dislikes} dislikes.')
    return movie_dislikes


@async_timer
async def get_user_bookmarks(client, user_id):
    user_bookmarks = await client.testDB.Bookmarks.count_documents({'user_id': user_id})
    print(f'User {user_id} has {user_bookmarks} bookmarks.')
    return user_bookmarks


@async_timer
async def remove_data(client):
    await client.testDB.Likes.drop()
    await client.testDB.Reviews.drop()
    await client.testDB.Bookmarks.drop()


async def main():
    client = await create_conn()
    client.close()


asyncio.run(main())
