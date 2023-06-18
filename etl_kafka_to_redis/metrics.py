import asyncio
import os

import psutil
from loguru import logger
from prometheus_client import Gauge, start_http_server
from settings import settings

mem_consumed_gauge = Gauge('memory_consumed_etl', 'Occupied memory for ETL process')


async def mem_health_monitor():
    start_http_server(settings.prometheus_port)
    logger.info('Health monitor started', extra={'tag': ['etl_app']})
    while True:
        try:
            pid = os.getpid()
            py = psutil.Process(pid)
            used = py.memory_info()
            if hasattr(used, 'data'):
                mem_consumed_gauge.set(used.data)
            else:
                logger.warning(
                    'Memory consuming doesnt supported for this OS',
                    extra={'tag': ['etl_app']},
                )
                break

        except asyncio.CancelledError as exc:
            raise exc

        except Exception:
            logger.error('Exception in mem health monitor', extra={'tag': ['etl_app']})

        await asyncio.sleep(settings.memory_monitor_interval)
