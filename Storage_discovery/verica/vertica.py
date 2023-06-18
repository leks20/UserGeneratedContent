import datetime
import logging
import random
import time
import uuid
from functools import wraps

import vertica_python


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        logging.info(
            'Function %s took %.4f seconds to execute', func.__name__, elapsed_time
        )
        return result

    return wrapper


connection_info = {
    'host': '127.0.0.1',
    'port': 5433,
    'user': 'dbadmin',
    'password': '',
    'database': 'docker',
    'autocommit': True,
}


def create_table():
    with vertica_python.connect(**connection_info) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE views (
                user_id UUID NOT NULL,
                movie_id UUID NOT NULL,
                progress FLOAT NOT NULL,
                event_time TIMESTAMP NOT NULL,
            );
            """
        )


@timer
def generate_data(n):
    return [
        (
            uuid.uuid4(),
            uuid.uuid4(),
            random.random(),  # noqa: S311
            datetime.datetime.now(),
        )
        for _ in range(n)
    ]


def insert_data(chunk):
    with vertica_python.connect(**connection_info) as connection:
        cursor = connection.cursor()
        insert_stmt = """
            INSERT INTO views (user_id, movie_id, progress, event_time)
            VALUES (%s, %s, %s, %s)
        """
        cursor.executemany(insert_stmt, chunk)


@timer
def process_data(n, chunk_size):
    data = generate_data(n)
    chunks = [data[i: i + chunk_size] for i in range(0, len(data), chunk_size)]
    for chunk in chunks:
        insert_data(chunk)


@timer
def select_data(limit):
    with vertica_python.connect(**connection_info) as connection:
        cursor = connection.cursor()
        select_stmt = 'SELECT * FROM views LIMIT %s'
        cursor.execute(select_stmt, [limit])
        return cursor.fetchall()
