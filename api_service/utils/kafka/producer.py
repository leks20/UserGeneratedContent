from aiokafka import AIOKafkaProducer

from conf.config import settings

producer: AIOKafkaProducer | None = None


async def get_producer() -> AIOKafkaProducer:
    if not producer:
        raise ValueError
    return producer


async def create_and_start_producer() -> None:
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_host,
    )
    await producer.start()


async def stop_producer() -> None:
    if not producer:
        return
    await producer.stop()
