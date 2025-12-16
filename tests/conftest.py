from typing import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine, make_url, URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
from sqlalchemy_utils import database_exists, drop_database, create_database

from src.dependencies import get_engine, get_session
from src.app import create_app
from src.config.settings import Settings
from src.repositories.tables import Base


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return Settings()


@pytest.fixture(scope="session")
def pg_url(test_settings: Settings) -> URL:
    return make_url(str(test_settings.postgres_dsn)).set(database="note-flow-test")


@pytest.fixture(scope="session")
def test_app(
    test_settings: Settings,
    get_async_engine: AsyncEngine,
    session_maker: async_sessionmaker[AsyncSession],
) -> FastAPI:
    app = create_app()
    app.dependency_overrides[get_engine] = lambda: get_async_engine
    app.dependency_overrides[get_session] = lambda: session_maker
    return app


@pytest.fixture(scope="session")
def create_db(pg_url):
    sync_engine = create_engine(pg_url.set(drivername="postgresql"))
    if database_exists(sync_engine.url):
        drop_database(sync_engine.url)
    create_database(sync_engine.url)
    Base.metadata.create_all(sync_engine)
    yield
    sync_engine.dispose()
    drop_database(sync_engine.url)


@pytest.fixture(scope="session")
async def get_async_engine(create_db, pg_url: URL) -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(pg_url, isolation_level='AUTOCOMMIT')
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
def session_maker(get_async_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=get_async_engine,
        expire_on_commit=False,
        autoflush=False,
    )


@pytest.fixture
async def db_session(session_maker: async_sessionmaker[AsyncSession]) -> AsyncIterator[AsyncSession]:
    async with session_maker() as session:
        async with session.begin():
            yield session


@pytest.fixture(autouse=True)
async def rollback_db(get_async_engine):
    yield
    async with get_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture
async def test_client(test_app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as client:
        yield client
