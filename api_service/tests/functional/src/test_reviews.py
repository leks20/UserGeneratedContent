from motor.motor_asyncio import AsyncIOMotorDatabase
from starlette.testclient import TestClient


async def test_add_review(
    client: TestClient,
    review_collection: AsyncIOMotorDatabase,
    review_url: str,
    review_data: dict,
):
    response = client.post(review_url, json=review_data)

    assert response.status_code == 200
    assert await review_collection.count_documents({}) == 1


def test_get_reviews(client: TestClient, review_url: str, prepare_reviews):
    response = client.get(review_url)
    assert response.status_code == 200
    assert len(response.json()['reviews']) == 2


async def test_like_review(client: TestClient, review_url: str, prepare_reviews):
    review_id = str((await prepare_reviews.find_one({}))['_id'])
    response = client.patch(f'{review_url}{review_id}/like')

    assert response.status_code == 200
    assert 'Like has been added to review' in response.json()['message']


async def test_dislike_review(client: TestClient, review_url: str, prepare_reviews):
    review_id = str((await prepare_reviews.find_one({}))['_id'])
    response = client.patch(f'{review_url}{review_id}/dislike')
    assert response.status_code == 200
    assert 'Dislike has been added to review' in response.json()['message']
