from typing import TypeVar

from pydantic import BaseModel
from redis.asyncio import Redis

from src.cache_entities.base import BaseCache

T = TypeVar("T", bound=BaseModel)


class RedisCacheRepository(BaseCache[T]):
    def __init__(self, redis: Redis) -> None:  # type: ignore[type-arg]
        self._redis = redis

    async def load(self, key: str, model: type[T]) -> T | None:
        raw = await self._redis.get(key)
        if raw is None:
            return None
        return model.model_validate_json(raw)

    async def store(self, key: str, value: T, ttl: int) -> None:
        await self._redis.set(key, value.model_dump_json(), ex=ttl)

    async def invalidate(self, key: str) -> None:
        await self._redis.delete(key)
