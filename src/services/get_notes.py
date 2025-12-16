from fastapi import HTTPException

from src.repositories.repository import AcquireNotesRepository
from src.schemas import NotesRow, NoteRow


class GetAllNotes:
    def __init__(self, notes_repo: AcquireNotesRepository):
        self._notes_repo = notes_repo

    async def __call__(self) -> list[NotesRow]:
        async with self._notes_repo() as notes_repo:
            notes = await notes_repo.get_notes_is_active()
            if not notes:
                raise HTTPException(status_code=404, detail="Notes not found")
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
