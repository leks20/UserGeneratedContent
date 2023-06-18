from pydantic import BaseSettings, validator


class ETLSettings(BaseSettings):
    kafka_host: str = 'kafka'
    kafka_port: int = 9092
    kafka_topic: str = 'watch_progress'

    redis_host: str = 'redis'
    redis_port: int = 6379

    prometheus_port: int = 8001
    memory_monitor_interval: int = 30  # в секундах

    @property
    def bootstrap_ulr(self):
        return f'{self.kafka_host}:{str(self.kafka_port)}'

    @property
    def redis_url(self):
        return f'redis://{self.redis_host}:{str(self.redis_port)}'

    @validator('kafka_topic', pre=True)
    def lowering_topic(cls, kafka_topic):  # noqa: N805
        return kafka_topic.lower()


settings = ETLSettings()
