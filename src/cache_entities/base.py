from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar("T")


class BaseCache[T](ABC):
    @abstractmethod
    async def load(self, key: str, model: type[T]) -> T | None: ...

    @abstractmethod
    async def store(self, key: str, value: T, ttl: int) -> None: ...

    @abstractmethod
    async def invalidate(self, key: str) -> None: ...
