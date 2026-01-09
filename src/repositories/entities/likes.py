from sqlalchemy import bindparam, select, func
from sqlalchemy.dialects.postgresql import insert

from src.schemas import LikeIdRow, LikesCountRow
from src.repositories.entities.mixin import QueryMixIn
from src.repositories.tables import Like


class CreateLike(QueryMixIn):
    QUERY = (
        insert(Like)
        .values(
            note_id=bindparam("note_id"),
            user_id=bindparam("user_id"),
        )
        .on_conflict_do_nothing(index_elements=["note_id", "user_id"])
        .returning(Like.c.id)
    )

    async def __call__(self, note_id: int, user_id: int) -> LikeIdRow | None:
        return await self.first_row_result(self.QUERY, LikeIdRow, note_id=note_id, user_id=user_id)


class GetLikesCount(QueryMixIn):
    QUERY = select(func.count(Like.c.id).label("likes")).where(Like.c.note_id == bindparam("note_id"))

    async def __call__(self, note_id: int) -> LikesCountRow | None:
        return await self.first_row_result(self.QUERY, LikesCountRow, note_id=note_id)
