import pytest
from httpx import AsyncClient
from app.config.database import Database

# Sample data for creating a cafe and a review
cafe_data = {
    "name": "Test Cafe for Reviews",
    "address": {
        "street": "456 Review Ave",
        "city": "Reviewville",
        "state": "RV",
        "zip_code": "54321"
    },
    "location": {
        "coordinates": [-74.0060, 40.7128]
    }
}

review_data = {
    "user_id": "test_user_123",
    "overall_rating": 4,
    "outlet_accessibility": 3,
    "wifi_quality": 2,
    "atmosphere": "Cozy and quiet",
}

@pytest.fixture(autouse=True)
async def cleanup():
    yield
    await Database.get_db().cafes.delete_many({})
    await Database.get_db().reviews.delete_many({})

async def create_test_cafe(client: AsyncClient):
    response = await client.post("/api/v1/cafes/", json=cafe_data)
    assert response.status_code == 200
    return response.json()

@pytest.mark.anyio
async def test_create_review(client: AsyncClient):
    cafe = await create_test_cafe(client)
    review_data_with_spot = {**review_data, "study_spot_id": cafe["_id"]}
    
    response = await client.post("/api/v1/reviews/", json=review_data_with_spot)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == review_data["user_id"]
    assert data["study_spot_id"] == cafe["_id"]
    assert "_id" in data

@pytest.mark.anyio
async def test_get_review(client: AsyncClient):
    cafe = await create_test_cafe(client)
    review_data_with_spot = {**review_data, "study_spot_id": cafe["_id"]}
    create_response = await client.post("/api/v1/reviews/", json=review_data_with_spot)
    review_id = create_response.json()["_id"]

    response = await client.get(f"/api/v1/reviews/{review_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["_id"] == review_id
    assert data["user_id"] == review_data["user_id"]

@pytest.mark.anyio
async def test_get_reviews_by_study_spot(client: AsyncClient):
    cafe = await create_test_cafe(client)
    review_data_with_spot = {**review_data, "study_spot_id": cafe["_id"]}
    await client.post("/api/v1/reviews/", json=review_data_with_spot)

    response = await client.get(f"/api/v1/reviews/by-spot/{cafe['_id']}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["study_spot_id"] == cafe["_id"]

@pytest.mark.anyio
async def test_update_review(client: AsyncClient):
    cafe = await create_test_cafe(client)
    review_data_with_spot = {**review_data, "study_spot_id": cafe["_id"]}
    create_response = await client.post("/api/v1/reviews/", json=review_data_with_spot)
    review_id = create_response.json()["_id"]

    update_data = {"atmosphere": "A bit too loud for my taste"}
    response = await client.put(f"/api/v1/reviews/{review_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["atmosphere"] == "A bit too loud for my taste"

@pytest.mark.anyio
async def test_delete_review(client: AsyncClient):
    cafe = await create_test_cafe(client)
    review_data_with_spot = {**review_data, "study_spot_id": cafe["_id"]}
    create_response = await client.post("/api/v1/reviews/", json=review_data_with_spot)
    review_id = create_response.json()["_id"]

    response = await client.delete(f"/api/v1/reviews/{review_id}")
    # The endpoint returns a 200 status code with a message on success
    assert response.status_code == 200

    # Verify it's deleted
    get_response = await client.get(f"/api/v1/reviews/{review_id}")
    assert get_response.status_code == 404

@pytest.mark.anyio
async def test_add_photo_to_review(client: AsyncClient):
    cafe = await create_test_cafe(client)
    review_data_with_spot = {**review_data, "study_spot_id": cafe["_id"]}
    create_response = await client.post("/api/v1/reviews/", json=review_data_with_spot)
    review_id = create_response.json()["_id"]

    photo_data = {"url": "http://example.com/photo.jpg", "caption": "My new favorite study spot!"}
    response = await client.post(f"/api/v1/reviews/{review_id}/photos", json=photo_data)
    assert response.status_code == 200
    data = response.json()
    assert "photos" in data
    assert len(data["photos"]) > 0
    assert data["photos"][0]["url"] == photo_data["url"] 