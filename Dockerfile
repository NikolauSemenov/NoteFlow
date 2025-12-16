FROM python:3.12.6-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ARG POETRY_VERSION=2.2.1

WORKDIR /app

RUN pip install --upgrade pip wheel "poetry==${POETRY_VERSION}"
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY src /app/
COPY alembic.ini /app/
COPY migrations /app/migrations


CMD ["uvicorn", "src.app:create_app", "--host", "0.0.0.0", "--port", "8000"]