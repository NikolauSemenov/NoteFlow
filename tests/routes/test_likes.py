from httpx import AsyncClient


async def test_create_like(test_client: AsyncClient, create_note):
    response = await test_client.post(
        "/note-flow/api/v1/note/like",
        json={"note_id": create_note},
        headers={"X-User-ID": "1"},
    )
    assert response.status_code == 201
    assert response.json() == {"likes": 1}
