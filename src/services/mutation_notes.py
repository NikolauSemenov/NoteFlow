from fastapi import HTTPException

from src.schemas import NoteIdRow, CreateNoteBody
from src.repositories.repository import MutatorNotesRepository


class TakeDownActiveNote:
    def __init__(self, notes_repo: MutatorNotesRepository):
        self._notes_repo = notes_repo

    async def __call__(self, note_id: int) -> NoteIdRow | None:
        async with self._notes_repo() as notes_repo:
            note = await notes_repo.takedown_note(note_id)
            if note is None:
                raise HTTPException(status_code=404, detail=f"Note {note_id} not found")
            return note


class CreateNote:
    def __init__(self, notes_repo: MutatorNotesRepository):
        self._notes_repo = notes_repo

    async def __call__(self, note: CreateNoteBody) -> NoteIdRow | None:
        async with self._notes_repo() as notes_repo:
            return await notes_repo.create_note(title=note.title, content=note.content)
