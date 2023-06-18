import logging
import time
from functools import wraps

from clickhouse_driver import Client
from config import clickhouse_settings

client = Client(host=clickhouse_settings.clickhouse_node1_host)


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


@timer
def insert_data():
    for _ in range(10000):
        client.execute(
            """
            INSERT INTO default.movie_watch_events
            (user_id, movie_id, progress, event_time)
            SELECT
                generateUUIDv4(),
                generateUUIDv4(),
                rand() / CAST(0xFFFFFFFF as Float32),
                now()
            FROM numbers(1000)
            """
        )


@timer
def select_data(limit):
    result = client.execute('SELECT * FROM default.movie_watch_events LIMIT %s', limit)
    return result
