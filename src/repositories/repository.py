from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.entities.notes import GetNotesAllIsActive, GetNote, TakeDownNote, CreateNote
from src.repositories.utils import AcquireRepository, AcquireTxRepository


class NotesReaderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.get_notes_is_active = GetNotesAllIsActive(session)
        self.get_note = GetNote(session)


class NotesWriterRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.takedown_note = TakeDownNote(session)
        self.create_note = CreateNote(session)


AcquireNotesRepository = AcquireRepository[NotesReaderRepository]
MutatorNotesRepository = AcquireTxRepository[NotesWriterRepository]
