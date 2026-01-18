from httpx import AsyncClient


async def test_create_comment(test_client: AsyncClient, create_note):
    response = await test_client.post(
        "/note-flow/api/v1/note/comment",
        json={"note_id": create_note, "text": "test comment", "user_full_name": "Ivan Ivanov"},
        headers={"X-User-ID": "1"},
    )
    assert response.status_code == 201
    assert response.json() == {"id": 1}


async def test_delete_comment_success(test_client: AsyncClient, create_comment):
    response = await test_client.delete(
        f"/note-flow/api/v1/note/comment/{create_comment}",
        headers={"X-User-ID": "1"},
    )
    assert response.status_code == 200
    assert response.json() == {"id": create_comment}


async def test_delete_comment_not_found(test_client: AsyncClient):
    response = await test_client.delete(
        "/note-flow/api/v1/note/comment/999",
        headers={"X-User-ID": "1"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Comment 999 not found or you don't have permission to delete it"}


async def test_delete_comment_wrong_user(test_client: AsyncClient, create_comment):
    response = await test_client.delete(
        f"/note-flow/api/v1/note/comment/{create_comment}",
        headers={"X-User-ID": "2"},
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": f"Comment {create_comment} not found or you don't have permission to delete it"
    }


async def test_delete_comment_invalid_id(test_client: AsyncClient):
    response = await test_client.delete(
        "/note-flow/api/v1/note/comment/0",
        headers={"X-User-ID": "1"},
    )
    assert response.status_code == 422
