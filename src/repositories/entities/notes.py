from sqlalchemy import select, bindparam
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.entities.mixin import SelectableMixIn
from src.repositories.tables import Notes
from src.types import NotesRow, NoteRow


class GetNotesAllIsActive(SelectableMixIn):
    QUERY = select(Notes).where(Notes.is_active.is_(True)).order_by(Notes.id.desc())

    def __init__(self, session: AsyncSession):
        self.session = session

    async def __call__(self) -> list[NotesRow]:
        return await self.many_row_result(self.QUERY, NotesRow)


class GetNote(SelectableMixIn):
    QUERY = select(Notes).where(Notes.id == bindparam("note_id"))

    def __init__(self, session: AsyncSession):
        self.session = session

    async def __call__(self, note_id: int) -> NoteRow | None:
        return await self.one_row_result(self.QUERY, NoteRow, note_id=note_id)
