from httpx import AsyncClient


async def test_create_comment(test_client: AsyncClient, create_note):
    response = await test_client.post(
        "/note-flow/api/v1/note/comment",
        json={"note_id": create_note, "text": "test comment", "user_full_name": "Ivan Ivanov"},
        headers={"X-User-ID": "1"},
    )
    assert response.status_code == 201
    assert response.json() == {"id": 1}
