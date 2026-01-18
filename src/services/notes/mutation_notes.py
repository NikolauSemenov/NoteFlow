from fastapi import HTTPException

from src.cache_entities.notes import RedisCacheRepository
from src.config.settings import Settings
from src.repositories.repository import MutatorNotesRepository
from src.schemas import CreateNoteBody, NoteIdRow, NoteResultRow


class TakeDownActiveNote:
    def __init__(
        self,
        notes_repo: MutatorNotesRepository,
        cache: RedisCacheRepository[NoteResultRow],
        settings: Settings,
    ):
        self._notes_repo = notes_repo
        self._cache = cache
        self._settings = settings

    async def __call__(self, note_id: int, user_id: int) -> NoteIdRow | None:
        async with self._notes_repo() as notes_repo:
            note = await notes_repo.takedown_note(note_id, user_id)
            if note is None:
                raise HTTPException(status_code=404, detail=f"Note {note_id} not found")
            await self._cache.invalidate(self._settings.redis_notes_prefix)
            return note


class CreateNote:
    def __init__(
        self,
        notes_repo: MutatorNotesRepository,
        cache: RedisCacheRepository[NoteResultRow],
        settings: Settings,
    ):
        self._notes_repo = notes_repo
        self._cache = cache
        self._settings = settings

    async def __call__(self, note: CreateNoteBody, user_id: int) -> NoteIdRow | None:
        async with self._notes_repo() as notes_repo:
            result = await notes_repo.create_note(
                title=note.title,
                content=note.content,
                user_full_name=note.full_name,
                user_id=user_id,
            )
            await self._cache.invalidate(self._settings.redis_notes_prefix)
            return result


class DeleteNote:
    def __init__(
        self,
        notes_repo: MutatorNotesRepository,
        cache: RedisCacheRepository[NoteResultRow],
        settings: Settings,
    ):
        self._notes_repo = notes_repo
        self._cache = cache
        self._settings = settings

    async def __call__(self, note_id: int, user_id: int) -> NoteIdRow | None:
        async with self._notes_repo() as notes_repo:
            note = await notes_repo.delete_note(note_id, user_id)
            if note is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Note {note_id} not found or you don't have permission to delete it",
                )
            await self._cache.invalidate(self._settings.redis_notes_prefix)
            return note
