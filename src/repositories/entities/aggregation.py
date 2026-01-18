from sqlalchemy import bindparam, select
from sqlalchemy.sql.functions import count, func

from src.repositories.entities.mixin import QueryMixIn
from src.repositories.tables import Comment, Like, Note
from src.schemas import NoteRow, NotesRow

_comments_subquery = (
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

_likes_subquery = select(Like.c.note_id, count(Like.c.id).label("likes")).group_by(Like.c.note_id).subquery()


class GetNotesAllIsActive(QueryMixIn):
    QUERY = (
        select(
            Note,
            func.coalesce(_likes_subquery.c.likes, 0).label("likes"),
            func.coalesce(_comments_subquery.c.comments, func.jsonb_build_array()).label("comments"),
        )
        .outerjoin(_likes_subquery, _likes_subquery.c.note_id == Note.c.id)
        .outerjoin(_comments_subquery, _comments_subquery.c.note_id == Note.c.id)
        .where(Note.c.is_active.is_(True))
        .order_by(Note.c.id.desc())
    )

    async def __call__(self) -> list[NotesRow]:
        return await self.many_row_result(self.QUERY, NotesRow)


class GetNote(QueryMixIn):
    QUERY = (
        select(
            Note,
            func.coalesce(_likes_subquery.c.likes, 0).label("likes"),
            func.coalesce(_comments_subquery.c.comments, func.jsonb_build_array()).label("comments"),
        )
        .where(Note.c.id == bindparam("note_id"))
        .outerjoin(_likes_subquery, _likes_subquery.c.note_id == Note.c.id)
        .outerjoin(_comments_subquery, _comments_subquery.c.note_id == Note.c.id)
    )

    async def __call__(self, note_id: int) -> NoteRow | None:
        return await self.first_row_result(self.QUERY, NoteRow, note_id=note_id)
