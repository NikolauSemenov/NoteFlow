from httpx import AsyncClient


async def test_get_notes(test_client: AsyncClient, create_note):
    response = await test_client.get("/note-flow/api/v1/notes")
    assert response.status_code == 200
    assert len(response.json()[0]) == 8


async def test_get_notes_not_found(test_client: AsyncClient):
    response = await test_client.get("/note-flow/api/v1/notes")
    assert response.status_code == 404
    assert response.json() == {"detail": "Notes not found"}


async def test_get_note_by_id(test_client: AsyncClient, create_note):
    response = await test_client.get(f"/note-flow/api/v1/note/{create_note}")
    assert response.status_code == 200
    assert len(response.json()) == 9


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
    """Test deletion of non-existent note"""
    response = await test_client.delete(
        "/note-flow/api/v1/note/999",
        headers={"X-User-ID": "1"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Note 999 not found or you don't have permission to delete it"}


async def test_delete_note_wrong_user(test_client: AsyncClient, create_note):
    """Test deletion of note by different user (no permission)"""
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
    # First verify comment exists
    response = await test_client.get(f"/note-flow/api/v1/note/{create_note}")
    assert response.status_code == 200
    note_data = response.json()
    assert len(note_data["comments"]) > 0

    # Delete the note
    response = await test_client.delete(
        f"/note-flow/api/v1/note/{create_note}",
        headers={"X-User-ID": "1"},
    )
    assert response.status_code == 200

    # Verify note is deleted
    response = await test_client.get(f"/note-flow/api/v1/note/{create_note}")
    assert response.status_code == 404
