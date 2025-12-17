from contextlib import asynccontextmanager
from typing import AsyncIterator

import redis.asyncio as redis
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession

from src.config.settings import settings


class AppResources:
    def __init__(self) -> None:
        self.redis: redis.Redis | None = None
        self.engine: AsyncEngine | None = None
        self.async_session_maker: async_sessionmaker[AsyncSession] | None = None

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
        )
        self.async_session_maker = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
            autoflush=False,
            autocommit=False,
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
