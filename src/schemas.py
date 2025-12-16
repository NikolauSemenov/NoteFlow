from pydantic import BaseModel


class NoteIdRow(BaseModel):
    id: int


class NotesRow(BaseModel):
    id: int
    title: str
    content: str


class NoteRow(NotesRow):
    is_active: bool
