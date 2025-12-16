import pytest
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.tables import Notes


@pytest.fixture
async def create_note(db_session: AsyncSession):
    result = await db_session.execute(
        insert(Notes).values(
            title="Test Note",
            content="Test Note content",
            is_active=True,
        ).returning(Notes.id)
    )
    return result.scalar()
