import json
from typing import TypeVar

from redis.asyncio import Redis
from pydantic import BaseModel

from src.cache_entities.base import BaseCache

T = TypeVar("T", bound=BaseModel)


class RedisCacheRepository(BaseCache[T]):
    def __init__(self, redis: Redis):
        self._redis = redis

    async def load(self, key: str, model: type[T]) -> T | None:
        raw = await self._redis.get(key)
        if raw is None:
            return None
        data = json.loads(raw)
        return model.model_validate(data)

    async def store(self, key: str, value: T, ttl: int) -> None:
        await self._redis.set(key, value=json.dumps(value.model_dump_json()), ex=ttl)

    async def invalidate(self, key: str) -> None:
        await self._redis.delete(key)
