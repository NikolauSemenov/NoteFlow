from sqlalchemy.ext.asyncio import AsyncConnection

from src.repositories.entities.aggregation import GetNotesAllIsActive, GetNote
from src.repositories.entities.likes import CreateLike, GetLikesCount
from src.repositories.entities.notes import TakeDownNote, CreateNote
from src.repositories.utils import AcquireRepository, AcquireTxRepository


class NotesReaderRepository:
    def __init__(self, conn: AsyncConnection) -> None:
        self.get_notes_is_active = GetNotesAllIsActive(conn)
        self.get_note = GetNote(conn)


class NotesWriterRepository:
    def __init__(self, conn: AsyncConnection) -> None:
        self.takedown_note = TakeDownNote(conn)
        self.create_note = CreateNote(conn)


class LikesReaderRepository:
    def __init__(self, conn: AsyncConnection) -> None:
        self.get_likes_count = GetLikesCount(conn)


class LikesWriterRepository:
    def __init__(self, conn: AsyncConnection) -> None:
        self.create_like = CreateLike(conn)


AcquireNotesRepository = AcquireRepository[NotesReaderRepository]
MutatorNotesRepository = AcquireTxRepository[NotesWriterRepository]

AcquireLikesRepository = AcquireRepository[LikesReaderRepository]
MutatorLikesRepository = AcquireTxRepository[LikesWriterRepository]
