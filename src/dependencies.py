from typing import Annotated, cast

from fastapi import Request
from fastapi.params import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine

from src.cache_entities.notes import RedisCacheRepository
from src.config.settings import Settings, settings
from src.repositories.repository import (
    AcquireNotesRepository,
    CommentWriterRepository,
    LikesWriterRepository,
    MutatorCommentRepository,
    MutatorLikesRepository,
    MutatorNotesRepository,
    NotesReaderRepository,
    NotesWriterRepository,
)
from src.schemas import NoteResultRow
from src.services.comments.mutation import CreateComment, DeleteComment
from src.services.likes.aggregation import CreateLike
from src.services.notes.get_notes import GetAllNotes, GetNote
from src.services.notes.mutation_notes import CreateNote, DeleteNote, TakeDownActiveNote


def get_settings() -> Settings:
    return settings


def get_engine(request: Request) -> AsyncEngine:
    return cast(AsyncEngine, request.app.state.resources.engine)


def get_redis(request: Request) -> Redis:  # type: ignore[type-arg]
    return cast(Redis, request.app.state.resources.redis)  # type: ignore[type-arg]


def get_redis_cache(
    redis_client: Annotated[Redis, Depends(get_redis)],  # type: ignore[type-arg]
) -> RedisCacheRepository[NoteResultRow]:
    return RedisCacheRepository(redis_client)


def get_notes_repository(
    engine: Annotated[AsyncEngine, Depends(get_engine)],
) -> AcquireNotesRepository:
    return AcquireNotesRepository(engine, NotesReaderRepository)


def mutator_notes_repository(
    engine: Annotated[AsyncEngine, Depends(get_engine)],
) -> MutatorNotesRepository:
    return MutatorNotesRepository(engine, NotesWriterRepository)


def get_notes(
    notes_repository: Annotated[AcquireNotesRepository, Depends(get_notes_repository)],
    cache_deps: Annotated[RedisCacheRepository[NoteResultRow], Depends(get_redis_cache)],
) -> GetAllNotes:
    return GetAllNotes(notes_repository, cache=cache_deps, setting=settings)


def get_note_by_id(
    notes_repository: Annotated[AcquireNotesRepository, Depends(get_notes_repository)],
) -> GetNote:
    return GetNote(notes_repository)


def update_note_active(
    notes_repository: Annotated[MutatorNotesRepository, Depends(mutator_notes_repository)],
    cache: Annotated[RedisCacheRepository[NoteResultRow], Depends(get_redis_cache)],
    app_settings: Annotated[Settings, Depends(get_settings)],
) -> TakeDownActiveNote:
    return TakeDownActiveNote(notes_repository, cache, app_settings)


def create_note(
    notes_repository: Annotated[MutatorNotesRepository, Depends(mutator_notes_repository)],
    cache: Annotated[RedisCacheRepository[NoteResultRow], Depends(get_redis_cache)],
    app_settings: Annotated[Settings, Depends(get_settings)],
) -> CreateNote:
    return CreateNote(notes_repository, cache, app_settings)


def mutator_likes_repository(
    engine: Annotated[AsyncEngine, Depends(get_engine)],
) -> MutatorLikesRepository:
    return MutatorLikesRepository(engine, LikesWriterRepository)


def create_like(
    likes_repository: Annotated[MutatorLikesRepository, Depends(mutator_likes_repository)],
) -> CreateLike:
    return CreateLike(likes_repository)


def mutation_comment_repository(
    engine: Annotated[AsyncEngine, Depends(get_engine)],
) -> MutatorCommentRepository:
    return MutatorCommentRepository(engine, CommentWriterRepository)


def create_comment(
    comment_repository: Annotated[MutatorCommentRepository, Depends(mutation_comment_repository)],
) -> CreateComment:
    return CreateComment(comment_repository)


def delete_comment(
    comment_repository: Annotated[MutatorCommentRepository, Depends(mutation_comment_repository)],
) -> DeleteComment:
    return DeleteComment(comment_repository)


def delete_note(
    notes_repository: Annotated[MutatorNotesRepository, Depends(mutator_notes_repository)],
    cache: Annotated[RedisCacheRepository[NoteResultRow], Depends(get_redis_cache)],
    app_settings: Annotated[Settings, Depends(get_settings)],
) -> DeleteNote:
    return DeleteNote(notes_repository, cache, app_settings)
