from pydantic.env_settings import BaseSettings


class CLickHouseSettings(BaseSettings):
    clickhouse_node1_host: str = 'localhost'


clickhouse_settings = CLickHouseSettings()
