from abc import ABC, abstractmethod
from typing import Any


class AsyncKeyValueService(ABC):
    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def put_data(self, key: str, data: Any) -> Any | None:
        pass

    @abstractmethod
    async def get_data(self, key: str) -> list[Any] | None:  # noqa: WPS463
        pass
