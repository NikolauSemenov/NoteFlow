from sqlalchemy import bindparam, update, insert, delete, and_

from src.repositories.entities.mixin import QueryMixIn
from src.repositories.tables import Note
from src.schemas import NoteIdRow


class TakeDownNote(QueryMixIn):
    QUERY = (
        update(Note)
        .where(and_(Note.c.id == bindparam("note_id"), Note.c.user_id == bindparam("b_user_id")))
        .values(is_active=False)
        .returning(Note.c.id)
    )

    async def __call__(self, note_id: int, user_id: int) -> NoteIdRow | None:
        return await self.first_row_result(self.QUERY, NoteIdRow, note_id=note_id, b_user_id=user_id)


class CreateNote(QueryMixIn):
    QUERY = (
        insert(Note)
        .values(
            title=bindparam("title"),
            content=bindparam("content"),
            user_id=bindparam("user_id"),
            user_full_name=bindparam("user_full_name"),
        )
        .returning(Note.c.id)
    )

    async def __call__(self, title: str, content: str, user_id: int, user_full_name: str) -> NoteIdRow | None:
        return await self.first_row_result(
            self.QUERY,
            NoteIdRow,
            title=title,
            content=content,
            user_id=user_id,
            user_full_name=user_full_name,
        )


class DeleteNote(QueryMixIn):
    QUERY = (
        delete(Note)
        .where(and_(Note.c.id == bindparam("note_id"), Note.c.user_id == bindparam("user_id")))
        .returning(Note.c.id)
    )

    async def __call__(self, note_id: int, user_id: int) -> NoteIdRow | None:
        return await self.first_row_result(self.QUERY, NoteIdRow, note_id=note_id, user_id=user_id)
