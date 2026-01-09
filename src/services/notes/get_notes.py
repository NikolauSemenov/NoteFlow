from fastapi import HTTPException

from src.cache_entities.notes import RedisCacheRepository
from src.config.settings import Settings
from src.repositories.repository import AcquireNotesRepository
from src.schemas import NotesRow, NoteResultRow, NoteRow


class GetAllNotes:
    def __init__(
        self, notes_repo: AcquireNotesRepository, cache: RedisCacheRepository[NoteResultRow], setting: Settings
    ):
        self._notes_repo = notes_repo
        self._cache = cache
        self._setting = setting

    async def __call__(self) -> list[NotesRow]:
        # if result := await self._cache.load(self._setting.redis_notes_prefix, NotesCache):
        #     return result.result
        async with self._notes_repo() as notes_repo:
            notes = await notes_repo.get_notes_is_active()
            if not notes:
                raise HTTPException(status_code=404, detail="Notes not found")
            await self._cache.store(
                self._setting.redis_notes_prefix, NoteResultRow(result=notes), self._setting.redis_notes_ttl
            )
            return notes


class GetNote:
    def __init__(self, notes_repo: AcquireNotesRepository):
        self._notes_repo = notes_repo

    async def __call__(self, note_id: int) -> NoteRow:
        async with self._notes_repo() as notes_repo:
            result = await notes_repo.get_note(note_id)
            if result is None:
                raise HTTPException(status_code=404, detail="Note not found")
            return result
