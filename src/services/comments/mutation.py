from fastapi import HTTPException

from src.repositories.repository import MutatorCommentRepository
from src.schemas import CommentIdRow, CreateCommentBody


class CreateComment:
    def __init__(self, comment_repo: MutatorCommentRepository):
        self._comment_repo = comment_repo

    async def __call__(self, body: CreateCommentBody, user_id: int) -> CommentIdRow | None:
        async with self._comment_repo() as comment_repo:
            return await comment_repo.create_comment(body.note_id, user_id, body.user_full_name, body.text)


class DeleteComment:
    def __init__(self, comment_repo: MutatorCommentRepository):
        self._comment_repo = comment_repo

    async def __call__(self, comment_id: int, user_id: int) -> CommentIdRow | None:
        async with self._comment_repo() as comment_repo:
            if comment := await comment_repo.delete_comment(comment_id, user_id):
                return comment
            raise HTTPException(status_code=404, detail=f"Comment {comment_id} not found or you don't have permission to delete it")
