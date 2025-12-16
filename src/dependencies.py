from functools import lru_cache
from typing import Annotated

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker

from src.services.update_notes import TakeDownActiveNote
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


async def get_notes_repository(
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
) -> AcquireNotesRepository:
    return AcquireNotesRepository(session, NotesReaderRepository)


async def mutator_notes_repository(
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
) -> MutatorNotesRepository:
    return MutatorNotesRepository(session, NotesWriterRepository)


async def get_notes(notes_repository: Annotated[AcquireNotesRepository, Depends(get_notes_repository)]) -> GetAllNotes:
    return GetAllNotes(notes_repository)


async def get_note_by_id(
    notes_repository: Annotated[AcquireNotesRepository, Depends(get_notes_repository)],
) -> GetNote | None:
    return GetNote(notes_repository)


async def update_note_active(
    notes_repository: Annotated[MutatorNotesRepository, Depends(mutator_notes_repository)],
) -> TakeDownActiveNote:
    return TakeDownActiveNote(notes_repository)
