from functools import lru_cache
from typing import Annotated, cast

from fastapi import Request
import redis.asyncio as redis
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker

from src.schemas import NoteResultRow
from src.cache_entities.notes import RedisCacheRepository
from src.services.update_notes import TakeDownActiveNote, CreateNote
from src.config.settings import settings
from src.repositories.repository import (
    AcquireNotesRepository,
    NotesReaderRepository,
    MutatorNotesRepository,
    NotesWriterRepository,
)
from src.services.get_notes import GetAllNotes, GetNote


@lru_cache
def get_engine() -> AsyncEngine:
    return create_async_engine(str(settings.postgres_dsn))


@lru_cache
def get_session(engine: Annotated[AsyncEngine, Depends(get_engine)]) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
        autoflush=False,
        autocommit=False,
    )


@lru_cache
def get_redis(request: Request) -> redis.Redis:
    return cast(redis.Redis, request.app.state.redis)


@lru_cache
def get_redis_cache(redis_deps: Annotated[redis.Redis, Depends(get_redis)]) -> RedisCacheRepository[BaseModel]:
    return RedisCacheRepository(redis_deps)


@lru_cache
def get_notes_repository(
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
) -> AcquireNotesRepository:
    return AcquireNotesRepository(session, NotesReaderRepository)


@lru_cache
def mutator_notes_repository(
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
) -> MutatorNotesRepository:
    return MutatorNotesRepository(session, NotesWriterRepository)


@lru_cache
def get_notes(
    notes_repository: Annotated[AcquireNotesRepository, Depends(get_notes_repository)],
    cache_deps: Annotated[RedisCacheRepository[NoteResultRow], Depends(get_redis_cache)],
) -> GetAllNotes:
    return GetAllNotes(notes_repository, cache=cache_deps, setting=settings)


@lru_cache
def get_note_by_id(
    notes_repository: Annotated[AcquireNotesRepository, Depends(get_notes_repository)],
) -> GetNote | None:
    return GetNote(notes_repository)


@lru_cache
def update_note_active(
    notes_repository: Annotated[MutatorNotesRepository, Depends(mutator_notes_repository)],
) -> TakeDownActiveNote:
    return TakeDownActiveNote(notes_repository)


@lru_cache
def create_note(
    notes_repository: Annotated[MutatorNotesRepository, Depends(mutator_notes_repository)],
) -> CreateNote:
    return CreateNote(notes_repository)
