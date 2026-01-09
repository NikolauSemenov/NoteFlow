from sqlalchemy import select, bindparam
from sqlalchemy.sql.functions import count, func

from src.repositories.entities.mixin import QueryMixIn
from src.repositories.tables import Note, Like, Comment
from src.schemas import NotesRow, NoteRow


class GetNotesAllIsActive(QueryMixIn):
    comments_subq = (
        select(
            Comment.c.note_id,
            func.jsonb_agg(
                func.jsonb_build_object(
                    "comment_id",
                    Comment.c.id,
                    "text",
                    Comment.c.text,
                    "user_name",
                    Comment.c.user_full_name,
                    "user_id",
                    Comment.c.user_id,
                )
            ).label("comments"),
        )
        .group_by(Comment.c.note_id)
        .subquery()
    )

    likes_subq = select(Like.c.note_id, count(Like.c.id).label("likes")).group_by(Like.c.note_id).subquery()

    QUERY = (
        select(
            Note,
            func.coalesce(likes_subq.c.likes, 0).label("likes"),
            func.coalesce(comments_subq.c.comments, func.jsonb_build_array()).label("comments"),
        )
        .outerjoin(likes_subq, likes_subq.c.note_id == Note.c.id)
        .outerjoin(comments_subq, comments_subq.c.note_id == Note.c.id)
        .where(Note.c.is_active.is_(True))
        .order_by(Note.c.id.desc())
    )

    async def __call__(self) -> list[NotesRow]:
        return await self.many_row_result(self.QUERY, NotesRow)


class GetNote(QueryMixIn):
    comments_subq = (
        select(
            Comment.c.note_id,
            func.jsonb_agg(
                func.jsonb_build_object(
                    "comment_id",
                    Comment.c.id,
                    "text",
                    Comment.c.text,
                    "user_name",
                    Comment.c.user_full_name,
                    "user_id",
                    Comment.c.user_id,
                )
            ).label("comments"),
        )
        .group_by(Comment.c.note_id)
        .subquery()
    )

    QUERY = (
        select(
            Note,
            count(Like.c.id).label("likes"),
            func.coalesce(comments_subq.c.comments, func.jsonb_build_array()).label("comments"),
        )
        .where(Note.c.id == bindparam("note_id"))
        .outerjoin(Like, Like.c.note_id == Note.c.id)
        .outerjoin(comments_subq, comments_subq.c.note_id == Note.c.id)
        .group_by(Note.c.id, comments_subq.c.comments)
    )

    async def __call__(self, note_id: int) -> NoteRow | None:
        return await self.first_row_result(self.QUERY, NoteRow, note_id=note_id)
