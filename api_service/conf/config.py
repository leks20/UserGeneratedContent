from pydantic.env_settings import BaseSettings


class Settings(BaseSettings):
    bind_ip: str = '127.0.0.1'
    bind_port: int = 8000
    web_concurrency: int = 1
    kafka_host: str = 'kafka:9092'
    jwt_secret_key: str = 'secret'
    access_token__expire_minutes: int = 30
    algorithm: str = 'HS256'
    memory_monitor_interval: int = 30  # в секундах
    sentry_dsn: str = 'https://24609dd09c9f4b5f83001cb413dc57f5@o4505237876244480.ingest.sentry.io/4505282515501056'  # noqa: E501
    logstash_handler_host: str = 'logstash'
    logstash_handler_port: int = 5044
    logstash_handler_version: int = 1


class RedisSettings(BaseSettings):
    host: str = 'redis'
    port: int = 6379

    @property
    def redis_url(self):
        return f'redis://{self.host}:{str(self.port)}'

    class Config:
        env_prefix = 'REDIS_'


class MongoSettings(BaseSettings):
    host: str = 'localhost'
    port: int = 27017
    db_name: str = 'UGC'

    @property
    def connect_ulr(self):
        return f'mongodb://{self.host}:{str(self.port)}'

    class Config:
        env_prefix = 'MONGO_'


settings = Settings()
redis_settings = RedisSettings()
mongo_settings = MongoSettings()
