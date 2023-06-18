import asyncio
import logging
import os
import random
import time
import uuid
from functools import wraps

import asyncpg
import faker


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
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    host = os.getenv('POSTGRES_SERVER')
    database = os.getenv('POSTGRES_DB')
    port = os.getenv('POSTGRES_PORT')

    return await asyncpg.connect(
        user=user,
        password=password,
        database=database,
        host=host,
        port=port,
    )


@async_timer
async def create_tables(conn):
    await conn.execute(
        """
            CREATE TABLE Likes (
                id SERIAL PRIMARY KEY,
                user_id UUID,
                movie_id UUID,
                rating INT CHECK (rating >= 0 AND rating <= 10)
            );
        """
    )

    await conn.execute(
        """
            CREATE TABLE Reviews (
                id SERIAL PRIMARY KEY,
                text TEXT,
                publication_date DATE,
                author VARCHAR(50),
                movie_id UUID
            );
        """
    )

    await conn.execute(
        """
            CREATE TABLE Bookmarks (
                id SERIAL PRIMARY KEY,
                user_id UUID,
                movie_id UUID
            );
        """
    )


@async_timer
async def insert_data(conn):
    fake = faker.Faker()

    unique_users = {str(uuid.uuid4()) for _ in range(100000)}
    unique_movies = {str(uuid.uuid4()) for _ in range(50000)}

    users_list = list(unique_users) * 10
    movies_list = list(unique_movies) * 20

    random.shuffle(users_list)
    random.shuffle(movies_list)

    likes_records = [
        (users_list[idx], movies_list[idx], random.randint(0, 10))  # noqa: S311
        for idx in range(1000000)
    ]

    await conn.executemany(
        """
            INSERT INTO Likes (user_id, movie_id, rating) VALUES ($1, $2, $3)
        """,
        likes_records,
    )

    reviews_records = [
        (
            fake.text(),
            fake.date_between(start_date='-1y', end_date='today'),
            fake.name(),
            str(uuid.uuid4()),
        )
        for _ in range(1000000)
    ]
    await conn.executemany(
        """
            INSERT INTO Reviews
            (text, publication_date, author, movie_id)
            VALUES ($1, $2, $3, $4)
        """,
        reviews_records,
    )

    bookmarks_records = [(str(uuid.uuid4()), str(uuid.uuid4())) for _ in range(1000000)]
    await conn.executemany(
        """
            INSERT INTO Bookmarks (user_id, movie_id) VALUES ($1, $2)
        """,
        bookmarks_records,
    )


@async_timer
async def read_data(conn):
    await conn.fetch('SELECT * FROM Likes')
    await conn.fetch('SELECT * FROM Reviews')
    await conn.fetch('SELECT * FROM Bookmarks')


@async_timer
async def remove_data(conn):
    await conn.execute('TRUNCATE TABLE Likes, Reviews, Bookmarks CASCADE')


@async_timer
async def average_user_rating(conn, movie_id):
    avg_rating = await conn.fetchval(
        """
            SELECT AVG(rating)
            FROM Likes
            WHERE movie_id = $1
        """,
        str(movie_id),
    )
    print(f'Average rating for movie {movie_id} is {avg_rating}')


@async_timer
async def get_user_likes(conn, user_id):
    user_likes = await conn.fetch(
        """
            SELECT movie_id, rating
            FROM Likes
            WHERE user_id = $1 AND rating > 8
        """,
        str(user_id),
    )
    return user_likes


@async_timer
async def get_movie_likes(conn, movie_id):
    movie_likes = await conn.fetchval(
        """
            SELECT COUNT(*)
            FROM Likes
            WHERE movie_id = $1 AND rating > 8
        """,
        str(movie_id),
    )
    logging.info('Movie %s has %s likes.', movie_id, movie_likes)
    return movie_likes


@async_timer
async def get_movie_dislikes(conn, movie_id):
    movie_dislikes = await conn.fetchval(
        """
            SELECT COUNT(*)
            FROM Likes
            WHERE movie_id = $1 AND rating < 2
        """,
        str(movie_id),
    )
    logging.info('Movie %s has %s dislikes.', movie_id, movie_dislikes)
    return movie_dislikes


@async_timer
async def get_user_bookmarks(conn, user_id):
    user_bookmarks = await conn.fetchval(
        """
            SELECT COUNT(*)
            FROM Bookmarks
            WHERE user_id = $1
        """,
        str(user_id),
    )
    print(f'User {user_id} has {user_bookmarks} bookmarks.')
    return user_bookmarks


async def main():
    conn = await create_conn()
    await get_user_bookmarks(conn, 'c79bedc9-dcde-4dbd-9683-46ce4ec3f7a6')
    await conn.close()


asyncio.run(main())
