from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI
from redis.asyncio import Redis

from src.config.settings import settings
from src.api.v1.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.redis = Redis.from_url(
        settings.redis_dsn.unicode_string(),
        decode_responses=True,
    )
    await app.state.redis.ping()
    yield
    await app.state.redis.close()


def create_app() -> FastAPI:
    app = FastAPI(
        docs_url=f"{settings.api_prefix}/docs",
        redoc_url=f"{settings.api_prefix}/redoc",
        openapi_url=f"{settings.api_prefix}/openapi.json",
        lifespan=lifespan,
    )

    app.include_router(router, prefix=settings.api_prefix)
    return app


if __name__ == "__main__":
    uvicorn.run(create_app, host=settings.host, port=settings.port)
