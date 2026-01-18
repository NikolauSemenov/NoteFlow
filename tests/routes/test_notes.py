import redis.asyncio as aioredis
from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncConnection

from src.config.settings import settings
from src.repositories.tables import Note


async def test_get_notes(test_client: AsyncClient, create_note):
    response = await test_client.get("/note-flow/api/v1/notes")
    assert response.status_code == 200
    note = response.json()[0]
    assert len(note) == 8


async def test_get_notes_not_found(test_client: AsyncClient):
    response = await test_client.get("/note-flow/api/v1/notes")
    assert response.status_code == 404
    assert response.json() == {"detail": "Notes not found"}


async def test_get_note_by_id(test_client: AsyncClient, create_note):
    response = await test_client.get(f"/note-flow/api/v1/note/{create_note}")
    assert response.status_code == 200
    note = response.json()
    assert len(note) == 9


async def test_get_note_by_id_not_found(test_client: AsyncClient, create_note):
    response = await test_client.get(f"/note-flow/api/v1/note/{create_note + 1}")
    assert response.status_code == 404


async def test_update_active_note(test_client: AsyncClient, create_note):
    response = await test_client.put(
        "/note-flow/api/v1/note/active",
        params={"id": create_note},
        headers={"X-User-ID": "1"},
    )
    assert response.status_code == 200
    assert response.json() == {"id": create_note}


async def test_update_active_note_not_found(test_client: AsyncClient):
    response = await test_client.put(
        "/note-flow/api/v1/note/active",
        params={"id": 1},
        headers={"X-User-ID": "1"},
    )
    assert response.status_code == 404


async def test_create_note(test_client: AsyncClient):
    response = await test_client.post(
        "/note-flow/api/v1/note",
        json={"title": "test title", "content": "test content", "full_name": "Test User"},
        headers={"X-User-ID": "1"},
    )
    assert response.status_code == 201
    assert response.json() == {"id": 1}


async def test_delete_note_success(test_client: AsyncClient, create_note):
    """Test successful deletion of own note"""
    response = await test_client.delete(
        f"/note-flow/api/v1/note/{create_note}",
        headers={"X-User-ID": "1"},
    )
    assert response.status_code == 200
    assert response.json() == {"id": create_note}


async def test_delete_note_not_found(test_client: AsyncClient):
    response = await test_client.delete(
        "/note-flow/api/v1/note/999",
        headers={"X-User-ID": "1"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Note 999 not found or you don't have permission to delete it"}


async def test_delete_note_wrong_user(test_client: AsyncClient, create_note):
    response = await test_client.delete(
        f"/note-flow/api/v1/note/{create_note}",
        headers={"X-User-ID": "2"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": f"Note {create_note} not found or you don't have permission to delete it"}


async def test_delete_note_invalid_id(test_client: AsyncClient):
    """Test deletion with invalid note ID"""
    response = await test_client.delete(
        "/note-flow/api/v1/note/0",
        headers={"X-User-ID": "1"},
    )
    assert response.status_code == 422


async def test_delete_note_cascades_comments(test_client: AsyncClient, create_note, create_comment):
    """Test that deleting a note also deletes its comments (cascade)"""
    response = await test_client.get(f"/note-flow/api/v1/note/{create_note}")
    assert response.status_code == 200
    note_data = response.json()
    assert len(note_data["comments"]) > 0

    response = await test_client.delete(
        f"/note-flow/api/v1/note/{create_note}",
        headers={"X-User-ID": "1"},
    )
    assert response.status_code == 200

    response = await test_client.get(f"/note-flow/api/v1/note/{create_note}")
    assert response.status_code == 404


async def test_get_notes_from_cache(
    test_client: AsyncClient,
    create_note: int,
    get_redis_test: aioredis.Redis,  # type: ignore[type-arg]
) -> None:
    response = await test_client.get("/note-flow/api/v1/notes")
    assert response.status_code == 200
    notes_from_db = response.json()
    assert len(notes_from_db) == 1

    cached_raw = await get_redis_test.get(settings.redis_notes_prefix)
    assert cached_raw is not None

    response = await test_client.get("/note-flow/api/v1/notes")
    assert response.status_code == 200
    notes_from_cache = response.json()

    assert notes_from_db == notes_from_cache


async def test_get_notes_cache_invalidation_on_create(
    test_client: AsyncClient,
    create_note: int,
    get_redis_test: aioredis.Redis,  # type: ignore[type-arg]
) -> None:
    response = await test_client.get("/note-flow/api/v1/notes")
    assert response.status_code == 200
    assert len(response.json()) == 1

    cached_before = await get_redis_test.get(settings.redis_notes_prefix)
    assert cached_before is not None

    response = await test_client.post(
        "/note-flow/api/v1/note",
        json={"title": "New Note", "content": "New content", "full_name": "Test User"},
        headers={"X-User-ID": "2"},
    )
    assert response.status_code == 201

    cached_after = await get_redis_test.get(settings.redis_notes_prefix)
    assert cached_after is None


async def test_get_notes_cache_invalidation_on_delete(
    test_client: AsyncClient,
    create_note: int,
    get_redis_test: aioredis.Redis,  # type: ignore[type-arg]
) -> None:
    response = await test_client.get("/note-flow/api/v1/notes")
    assert response.status_code == 200

    cached_before = await get_redis_test.get(settings.redis_notes_prefix)
    assert cached_before is not None

    response = await test_client.delete(
        f"/note-flow/api/v1/note/{create_note}",
        headers={"X-User-ID": "1"},
    )
    assert response.status_code == 200

    cached_after = await get_redis_test.get(settings.redis_notes_prefix)
    assert cached_after is None


async def test_get_notes_cache_invalidation_on_takedown(
    test_client: AsyncClient,
    create_note: int,
    get_redis_test: aioredis.Redis,  # type: ignore[type-arg]
) -> None:
    response = await test_client.get("/note-flow/api/v1/notes")
    assert response.status_code == 200

    cached_before = await get_redis_test.get(settings.redis_notes_prefix)
    assert cached_before is not None

    response = await test_client.put(
        "/note-flow/api/v1/note/active",
        params={"id": create_note},
        headers={"X-User-ID": "1"},
    )
    assert response.status_code == 200

    cached_after = await get_redis_test.get(settings.redis_notes_prefix)
    assert cached_after is None


async def test_cache_returns_same_data_without_db_query(
    test_client: AsyncClient,
    create_note: int,
    get_redis_test: aioredis.Redis,  # type: ignore[type-arg]
    db_connection: AsyncConnection,
) -> None:
    response = await test_client.get("/note-flow/api/v1/notes")
    assert response.status_code == 200
    original_notes = response.json()
    original_title = original_notes[0]["title"]

    await db_connection.execute(update(Note).where(Note.c.id == create_note).values(title="Changed Title"))

    response = await test_client.get("/note-flow/api/v1/notes")
    assert response.status_code == 200
    cached_notes = response.json()

    assert cached_notes[0]["title"] == original_title
    assert cached_notes[0]["title"] != "Changed Title"
