from collections.abc import AsyncIterator, Iterator

import pytest
import redis.asyncio as aioredis
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import URL, create_engine, make_url
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine
from sqlalchemy_utils import create_database, database_exists, drop_database

from src.app import create_app
from src.config.settings import Settings
from src.dependencies import get_engine, get_redis
from src.repositories.tables import metadata


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


@pytest.fixture(scope="session")
def pg_url(test_settings: Settings) -> URL:
    return make_url(test_settings.postgres_dsn.unicode_string()).set(database="note-flow-test")


@pytest.fixture(scope="session")
async def get_redis_test(test_settings: Settings) -> AsyncIterator[aioredis.Redis]:  # type: ignore[type-arg]
    redis_client = aioredis.Redis.from_url(
        f"{test_settings.redis_dsn.unicode_string()}/3",
        decode_responses=True,
    )
    yield redis_client
    await redis_client.aclose()


@pytest.fixture(scope="session")
def test_app(
    test_settings: Settings,
    get_async_engine: AsyncEngine,
    get_redis_test: aioredis.Redis,  # type: ignore[type-arg]
) -> FastAPI:
    app = create_app()
    app.dependency_overrides[get_engine] = lambda: get_async_engine
    app.dependency_overrides[get_redis] = lambda: get_redis_test
    return app


@pytest.fixture(scope="session")
def create_db(pg_url: URL) -> Iterator[None]:
    sync_engine = create_engine(pg_url.set(drivername="postgresql"))
    if database_exists(sync_engine.url):
        drop_database(sync_engine.url)
    create_database(sync_engine.url)
    metadata.create_all(sync_engine)
    yield
    sync_engine.dispose()
    drop_database(sync_engine.url)


@pytest.fixture(scope="session")
async def get_async_engine(create_db: Iterator[None], pg_url: URL) -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(pg_url, isolation_level="AUTOCOMMIT")
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_connection(get_async_engine: AsyncEngine) -> AsyncIterator[AsyncConnection]:
    async with get_async_engine.begin() as conn:
        yield conn


@pytest.fixture(autouse=True)
async def rollback_db(
    get_async_engine: AsyncEngine,
    get_redis_test: aioredis.Redis,  # type: ignore[type-arg]
) -> AsyncIterator[None]:
    yield
    async with get_async_engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)
    await get_redis_test.flushdb()


@pytest.fixture
async def test_client(test_app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as client:
        yield client
