from sqlalchemy import select, bindparam
from sqlalchemy.sql.functions import count

from src.repositories.entities.mixin import QueryMixIn
from src.repositories.tables import Note, Like
from src.schemas import NotesRow, NoteRow


class GetNotesAllIsActive(QueryMixIn):
    QUERY = (
        select(Note, count(Like.c.id).label("likes"))
        .where(Note.c.is_active.is_(True))
        .outerjoin(Like, Like.c.note_id == Note.c.id)
        .order_by(Note.c.id.desc())
        .group_by(Note.c.id)
    )

    async def __call__(self) -> list[NotesRow]:
        return await self.many_row_result(self.QUERY, NotesRow)


class GetNote(QueryMixIn):
    QUERY = (
        select(Note, count(Like.c.id).label("likes"))
        .where(Note.c.id == bindparam("note_id"))
        .outerjoin(Like, Like.c.note_id == Note.c.id)
        .group_by(Note.c.id)
    )

    async def __call__(self, note_id: int) -> NoteRow | None:
        return await self.first_row_result(self.QUERY, NoteRow, note_id=note_id)
