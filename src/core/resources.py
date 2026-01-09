from contextlib import asynccontextmanager
from typing import AsyncIterator

import redis.asyncio as redis
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.config.settings import settings


class AppResources:
    def __init__(self) -> None:
        self.redis: redis.Redis | None = None
        self.engine: AsyncEngine | None = None

    async def init_redis(self) -> None:
        self.redis = redis.Redis.from_url(
            settings.redis_dsn.unicode_string(),
            decode_responses=True,
        )
        if not await self.redis.ping():  # type: ignore[misc]
            raise RuntimeError("Redis is not connected")

    async def init_pg(self) -> None:
        self.engine = create_async_engine(
            settings.postgres_dsn.unicode_string(),
            echo=False,  # True для логов SQL
            pool_size=20,  # Максимум соединений в пуле
            max_overflow=10,  # Дополнительные соединения сверх pool_size
            pool_timeout=30,  # Время ожидания свободного соединения из пула (сек)
            pool_recycle=1800,  # Время жизни соединения (сек)
            pool_pre_ping=True,  # Проверка соединения перед использованием
        )

    async def close(self) -> None:
        if self.redis:
            await self.redis.aclose()
        if self.engine:
            await self.engine.dispose()

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncIterator[None]:
        await self.init_redis()
        await self.init_pg()
        try:
            yield
        finally:
            await self.close()
