import asyncio
import os

import psutil
from prometheus_client import Gauge

from conf.config import settings
from webapp.logging import logger

mem_consumed_gauge = Gauge('memory_consumed', 'Occupied memory')

mem_consuming_task: asyncio.Task | None = None


async def mem_health_monitor():
    logger.info('Health monitor started', extra={'tag': ['fast_api_app']})

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
                    extra={'tag': ['fast_api_app']},
                )
                break

        except asyncio.CancelledError as exc:
            raise exc

        except Exception:
            logger.error(
                'Exception in mem health monitor', extra={'tag': ['fast_api_app']}
            )

        await asyncio.sleep(settings.memory_monitor_interval)


async def start_mem_monitoring():
    mem_consuming_task = asyncio.create_task(mem_health_monitor())
    return mem_consuming_task


def stop_mem_monitoring():
    if mem_consuming_task:
        if logger:
            logger.info('Health monitor stopped', extra={'tag': ['fast_api_app']})

        mem_consuming_task.cancel()
