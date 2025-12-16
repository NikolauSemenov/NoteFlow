import uvicorn
from fastapi import FastAPI

from src.config.settings import settings
from src.api.v1.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        docs_url=f"{settings.api_prefix}/docs",
        redoc_url=f"{settings.api_prefix}/redoc",
        openapi_url=f"{settings.api_prefix}/openapi.json",
    )

    app.include_router(router, prefix=settings.api_prefix)
    return app


if __name__ == "__main__":
    uvicorn.run(create_app, host=settings.host, port=settings.port)
