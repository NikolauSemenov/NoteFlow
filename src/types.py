from typing import TYPE_CHECKING

from pydantic import PositiveInt, BaseModel

if TYPE_CHECKING:
    SerialInt = int
else:

    class SerialInt(PositiveInt):
        le = 2147483647


class NotesRow(BaseModel):
    id: int
    title: str
    content: str


class NoteRow(NotesRow):
    is_active: bool
