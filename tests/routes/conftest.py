import pytest
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncConnection

from src.repositories.tables import Note, Comment


@pytest.fixture
async def create_note(db_connection: AsyncConnection):
    result = await db_connection.execute(
        insert(Note)
        .values(
            title="Test Note",
            content="Test Note content",
            user_full_name="Ivan Ivanov",
            user_id=1,
            is_active=True,
        )
        .returning(Note.c.id)
    )
    return result.scalar()


@pytest.fixture
async def create_comment(db_connection: AsyncConnection, create_note: int):
    result = await db_connection.execute(
        insert(Comment)
        .values(
            note_id=create_note,
            text="Test Comment",
            user_full_name="Ivan Ivanov",
            user_id=1,
        )
        .returning(Comment.c.id)
    )
    return result.scalar()
