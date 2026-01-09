from httpx import AsyncClient


async def test_get_notes(test_client: AsyncClient, create_note):
    response = await test_client.get("/note-flow/api/v1/notes")
    assert response.status_code == 200
    assert len(response.json()[0]) == 7


async def test_get_notes_not_found(test_client: AsyncClient):
    response = await test_client.get("/note-flow/api/v1/notes")
    assert response.status_code == 404
    assert response.json() == {"detail": "Notes not found"}


async def test_get_note_by_id(test_client: AsyncClient, create_note):
    response = await test_client.get(f"/note-flow/api/v1/note/{create_note}")
    assert response.status_code == 200
    assert len(response.json()) == 8


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
