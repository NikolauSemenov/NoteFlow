from functools import lru_cache
from typing import Annotated, cast

from fastapi import Request
import redis.asyncio as redis
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncEngine

from src.schemas import NoteResultRow
from src.cache_entities.notes import RedisCacheRepository
from src.services.comments.mutation import CreateComment, DeleteComment
from src.services.likes.aggregation import CreateLike
from src.services.notes.mutation_notes import TakeDownActiveNote, CreateNote, DeleteNote
from src.config.settings import settings
from src.repositories.repository import (
    AcquireNotesRepository,
    NotesReaderRepository,
    MutatorNotesRepository,
    NotesWriterRepository,
    MutatorLikesRepository,
    LikesWriterRepository,
    AcquireLikesRepository,
    LikesReaderRepository,
    MutatorCommentRepository,
    CommentWriterRepository,
)
from src.services.notes.get_notes import GetAllNotes, GetNote


def get_engine(request: Request) -> AsyncEngine:
    return cast(AsyncEngine, request.app.state.resources.engine)


def get_redis(request: Request) -> redis.Redis:
    return cast(redis.Redis, request.app.state.resources.redis)


@lru_cache
def get_redis_cache(redis_deps: Annotated[redis.Redis, Depends(get_redis)]) -> RedisCacheRepository[BaseModel]:
    return RedisCacheRepository(redis_deps)


@lru_cache
def get_notes_repository(
    engine: Annotated[AsyncEngine, Depends(get_engine)],
) -> AcquireNotesRepository:
    return AcquireNotesRepository(engine, NotesReaderRepository)


@lru_cache
def mutator_notes_repository(
    engine: Annotated[AsyncEngine, Depends(get_engine)],
) -> MutatorNotesRepository:
    return MutatorNotesRepository(engine, NotesWriterRepository)


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


@lru_cache
def mutator_likes_repository(
    engine: Annotated[AsyncEngine, Depends(get_engine)],
) -> MutatorLikesRepository:
    return MutatorLikesRepository(engine, LikesWriterRepository)


@lru_cache
def get_likes_repository(
    engine: Annotated[AsyncEngine, Depends(get_engine)],
) -> AcquireLikesRepository:
    return AcquireLikesRepository(engine, LikesReaderRepository)


@lru_cache
def create_like(
    likes_repository: Annotated[MutatorLikesRepository, Depends(mutator_likes_repository)],
    get_likes_repo: Annotated[AcquireLikesRepository, Depends(get_likes_repository)],
) -> CreateLike:
    return CreateLike(likes_repository, get_likes_repo)


@lru_cache
def mutation_comment_repository(
    engine: Annotated[AsyncEngine, Depends(get_engine)],
) -> MutatorCommentRepository:
    return MutatorCommentRepository(engine, CommentWriterRepository)


@lru_cache
def create_comment(
    comment_repository: Annotated[MutatorCommentRepository, Depends(mutation_comment_repository)],
) -> CreateComment:
    return CreateComment(comment_repository)


@lru_cache
def delete_comment(
    comment_repository: Annotated[MutatorCommentRepository, Depends(mutation_comment_repository)],
) -> DeleteComment:
    return DeleteComment(comment_repository)


@lru_cache
def delete_note(
    notes_repository: Annotated[MutatorNotesRepository, Depends(mutator_notes_repository)],
) -> DeleteNote:
    return DeleteNote(notes_repository)
