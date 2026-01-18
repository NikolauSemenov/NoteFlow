from sqlalchemy.ext.asyncio import AsyncConnection

from src.repositories.entities.aggregation import GetNote, GetNotesAllIsActive
from src.repositories.entities.comments import CreateComment, DeleteComment
from src.repositories.entities.likes import CreateLike, GetLikesCount
from src.repositories.entities.notes import CreateNote, DeleteNote, TakeDownNote
from src.repositories.utils import AcquireRepository, AcquireTxRepository


class NotesReaderRepository:
    def __init__(self, conn: AsyncConnection) -> None:
        self.get_notes_is_active = GetNotesAllIsActive(conn)
        self.get_note = GetNote(conn)


class NotesWriterRepository:
    def __init__(self, conn: AsyncConnection) -> None:
        self.takedown_note = TakeDownNote(conn)
        self.create_note = CreateNote(conn)
        self.delete_note = DeleteNote(conn)


class LikesWriterRepository:
    def __init__(self, conn: AsyncConnection) -> None:
        self.create_like = CreateLike(conn)
        self.get_likes_count = GetLikesCount(conn)


class CommentWriterRepository:
    def __init__(self, conn: AsyncConnection) -> None:
        self.create_comment = CreateComment(conn)
        self.delete_comment = DeleteComment(conn)


AcquireNotesRepository = AcquireRepository[NotesReaderRepository]
MutatorNotesRepository = AcquireTxRepository[NotesWriterRepository]

MutatorLikesRepository = AcquireTxRepository[LikesWriterRepository]

MutatorCommentRepository = AcquireTxRepository[CommentWriterRepository]
