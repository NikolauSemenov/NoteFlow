from src.repositories.repository import MutatorCommentRepository
from src.schemas import CommentIdRow, CreateCommentBody


class CreateComment:
    def __init__(self, comment_repo: MutatorCommentRepository):
        self._comment_repo = comment_repo

    async def __call__(self, body: CreateCommentBody, user_id: int) -> CommentIdRow | None:
        async with self._comment_repo() as comment_repo:
            return await comment_repo.create_comment(body.note_id, user_id, body.user_full_name, body.text)
