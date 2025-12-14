from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.entities.notes import GetNotesAllIsActive, GetNote
from src.repositories.utils import AcquireRepository


class NotesRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.get_notes_is_active = GetNotesAllIsActive(session)
        self.get_note = GetNote(session)


AcquireNotesRepository = AcquireRepository[NotesRepository]
