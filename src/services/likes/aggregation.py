from src.repositories.repository import MutatorLikesRepository, AcquireLikesRepository
from src.schemas import CreateLikeBody, LikesCountRow


class CreateLike:
    def __init__(self, mut_likes_repo: MutatorLikesRepository, get_likes_repo: AcquireLikesRepository):
        self._mut_likes_repo = mut_likes_repo
        self._get_likes_repo = get_likes_repo

    async def __call__(self, body: CreateLikeBody, user_id: int) -> LikesCountRow | None:
        async with self._mut_likes_repo() as mutation_likes, self._get_likes_repo() as likes:
            await mutation_likes.create_like(body.note_id, user_id)
            return await likes.get_likes_count(body.note_id)
