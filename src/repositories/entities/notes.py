from sqlalchemy import select, bindparam, update, insert

from src.repositories.entities.mixin import QueryMixIn
from src.repositories.tables import Notes
from src.schemas import NotesRow, NoteRow, NoteIdRow


class GetNotesAllIsActive(QueryMixIn):
    QUERY = select(Notes).where(Notes.is_active.is_(True)).order_by(Notes.id.desc())

    async def __call__(self) -> list[NotesRow]:
        return await self.many_row_result(self.QUERY, NotesRow)


class GetNote(QueryMixIn):
    QUERY = select(Notes).where(Notes.id == bindparam("note_id"))

    async def __call__(self, note_id: int) -> NoteRow | None:
        return await self.one_row_result(self.QUERY, NoteRow, note_id=note_id)


class TakeDownNote(QueryMixIn):
    QUERY = update(Notes).where(Notes.id == bindparam("note_id")).values(is_active=False).returning(Notes.id)

    async def __call__(self, note_id: int) -> NoteIdRow | None:
        return await self.first_row_result(self.QUERY, NoteIdRow, note_id=note_id)


class CreateNote(QueryMixIn):
    QUERY = insert(Notes).values(title=bindparam("title"), content=bindparam("content")).returning(Notes.id)

    async def __call__(self, title: str, content: str) -> NoteIdRow | None:
        return await self.first_row_result(self.QUERY, NoteIdRow, title=title, content=content)
