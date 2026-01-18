FROM python:3.12.6-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ARG POETRY_VERSION=2.2.1

WORKDIR /app

RUN pip install --upgrade pip wheel "poetry==${POETRY_VERSION}"
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

COPY --chown=appuser:appgroup src /app/src/
COPY --chown=appuser:appgroup alembic.ini /app/
COPY --chown=appuser:appgroup migrations /app/migrations

USER appuser

CMD ["uvicorn", "src.app:create_app", "--host", "0.0.0.0", "--port", "8000"]
