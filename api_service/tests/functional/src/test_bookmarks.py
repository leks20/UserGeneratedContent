from motor.motor_asyncio import AsyncIOMotorDatabase
from starlette.testclient import TestClient


async def test_add_bookmark(
    client: TestClient,
    bookmark_collection: AsyncIOMotorDatabase,
    bookmark_ulr: str,
    bookmark_data: dict,
):
    response = client.post(bookmark_ulr, json=bookmark_data)

    assert response.status_code == 200
    assert await bookmark_collection.count_documents({}) == 1


def test_get_bookmarks(client: TestClient, bookmark_ulr: str, prepare_bookmarks):
    response = client.get(bookmark_ulr)

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_delete_bookmark(
    client: TestClient, bookmark_ulr_delete: str, prepare_bookmarks
):
    response = client.delete(bookmark_ulr_delete)

    assert response.status_code == 200
    assert len(response.json()) == 1
