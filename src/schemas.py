from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class NoteIdRow(BaseModel):
    id: int


class CommentsRow(BaseModel):
    comment_id: int
    text: str
    user_name: str
    user_id: int


class NotesRow(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    user_full_name: str
    user_id: int
    likes: int
    comments: list[CommentsRow] | None


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
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1, max_length=10000)
    full_name: str = Field(..., min_length=1, max_length=255)

    @field_validator("title", "content", "full_name", mode="before")
    @classmethod
    def strip_whitespace(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip()
        return v


class CreateLikeBody(BaseModel):
    note_id: int


class LikeIdRow(BaseModel):
    id: int


class LikesCountRow(BaseModel):
    likes: int


class CommentIdRow(BaseModel):
    id: int


class CreateCommentBody(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    user_full_name: str = Field(..., min_length=1, max_length=255)
    note_id: int = Field(..., gt=0)

    @field_validator("text", "user_full_name", mode="before")
    @classmethod
    def strip_whitespace(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip()
        return v
