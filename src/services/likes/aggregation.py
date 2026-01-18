from src.repositories.repository import MutatorLikesRepository
from src.schemas import CreateLikeBody, LikesCountRow


class CreateLike:
    def __init__(self, likes_repo: MutatorLikesRepository):
        self._likes_repo = likes_repo

    async def __call__(self, body: CreateLikeBody, user_id: int) -> LikesCountRow | None:
        async with self._likes_repo() as likes_repo:
            await likes_repo.create_like(body.note_id, user_id)
            return await likes_repo.get_likes_count(body.note_id)
