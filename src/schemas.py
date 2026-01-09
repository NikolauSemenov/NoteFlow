from datetime import datetime

from pydantic import BaseModel, Field


class NoteIdRow(BaseModel):
    id: int


class NotesRow(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    full_name: str = Field(validation_alias="user_full_name")
    user_id: int
    likes: int


class NotesCache(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    full_name: str
    user_id: int


class NoteRow(NotesRow):
    is_active: bool


class NoteResultRow(BaseModel):
    result: list[NotesRow]


class CreateNoteBody(BaseModel):
    title: str
    content: str
    full_name: str


class CreateLikeBody(BaseModel):
    note_id: int


class LikeIdRow(BaseModel):
    id: int


class LikesCountRow(BaseModel):
    likes: int


class CommentIdRow(BaseModel):
    id: int


class CreateCommentBody(BaseModel):
    text: str
    user_full_name: str
    note_id: int
