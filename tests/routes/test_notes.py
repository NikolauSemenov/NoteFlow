from httpx import AsyncClient


async def test_get_notes(test_client: AsyncClient, create_note):
    response = await test_client.get("/note-flow/api/v1/notes")
    assert response.status_code == 200
    assert response.json() == [{"id": 1, "title": "Test Note", "content": "Test Note content"}]


async def test_get_notes_not_found(test_client: AsyncClient):
    response = await test_client.get("/note-flow/api/v1/notes")
    assert response.status_code == 404
    assert response.json() == {"detail": "Notes not found"}


async def test_get_note_by_id(test_client: AsyncClient, create_note):
    response = await test_client.get(f"/note-flow/api/v1/note/{create_note}")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "Test Note", "content": "Test Note content", "is_active": True}


async def test_get_note_by_id_not_found(test_client: AsyncClient, create_note):
    response = await test_client.get(f"/note-flow/api/v1/note/{create_note + 1}")
    assert response.status_code == 404


async def test_update_active_note(test_client: AsyncClient, create_note):
    response = await test_client.put("/note-flow/api/v1/note/active", params={"id": create_note})
    assert response.status_code == 200
    assert response.json() == {"id": create_note}


async def test_update_active_note_not_found(test_client: AsyncClient):
    response = await test_client.put("/note-flow/api/v1/note/active", params={"id": 1})
    assert response.status_code == 404
