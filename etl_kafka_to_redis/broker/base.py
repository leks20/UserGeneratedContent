from abc import ABC, abstractmethod


class BaseConsumer(ABC):
    @abstractmethod
    async def get_consumer(self):
        pass


class BaseConsumerService(ABC):
    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def get_records(self):
        pass

    async def commit_changes(self):  # noqa: B027
        pass
