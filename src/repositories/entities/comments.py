from sqlalchemy import insert, bindparam

from src.schemas import CommentIdRow
from src.repositories.entities.mixin import QueryMixIn
from src.repositories.tables import Comment


class CreateComment(QueryMixIn):
    QUERY = (
        insert(Comment)
        .values(
            note_id=bindparam("note_id"),
            user_id=bindparam("user_id"),
            user_full_name=bindparam("user_full_name"),
            text=bindparam("text"),
        )
        .returning(Comment.c.id)
    )

    async def __call__(self, note_id: int, user_id: int, user_full_name: str, text: str) -> CommentIdRow | None:
        return await self.first_row_result(
            self.QUERY, CommentIdRow, note_id=note_id, user_id=user_id, user_full_name=user_full_name, text=text
        )
