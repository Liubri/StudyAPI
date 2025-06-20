import pytest
from httpx import AsyncClient
from app.config.database import Database

# Sample data for creating a cafe
cafe_data = {
    "name": "Test Cafe",
    "address": {
        "street": "123 Test St",
        "city": "Testville",
        "state": "TS",
        "zip_code": "12345"
    },
    "location": {
        "coordinates": [-73.9857, 40.7484]
    },
    "amenities": ["wifi", "power_outlets"],
    "wifi_access": 3,
    "outlet_accessibility": 3,
    "average_rating": 5
}

@pytest.fixture(autouse=True)
async def cleanup():
    yield
    await Database.get_db().cafes.delete_many({})

@pytest.mark.anyio
async def test_create_cafe(client: AsyncClient):
    response = await client.post("/api/v1/cafes/", json=cafe_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == cafe_data["name"]
    assert data["address"]["city"] == "Testville"
    assert "_id" in data

@pytest.mark.anyio
async def test_get_all_cafes(client: AsyncClient):
    # Create a cafe first
    await client.post("/api/v1/cafes/", json=cafe_data)
    
    response = await client.get("/api/v1/cafes/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == cafe_data["name"]

@pytest.mark.anyio
async def test_get_cafe(client: AsyncClient):
    # Create a cafe first
    create_response = await client.post("/api/v1/cafes/", json=cafe_data)
    cafe_id = create_response.json()["_id"]

    response = await client.get(f"/api/v1/cafes/{cafe_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == cafe_data["name"]
    assert data["_id"] == cafe_id

@pytest.mark.anyio
async def test_update_cafe(client: AsyncClient):
    # Create a cafe first
    create_response = await client.post("/api/v1/cafes/", json=cafe_data)
    cafe_id = create_response.json()["_id"]

    update_data = {"name": "Updated Test Cafe"}
    response = await client.put(f"/api/v1/cafes/{cafe_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Test Cafe"
    assert data["_id"] == cafe_id

@pytest.mark.anyio
async def test_delete_cafe(client: AsyncClient):
    # Create a cafe first
    create_response = await client.post("/api/v1/cafes/", json=cafe_data)
    cafe_id = create_response.json()["_id"]

    response = await client.delete(f"/api/v1/cafes/{cafe_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Cafe deleted successfully"

    # Verify it's deleted
    get_response = await client.get(f"/api/v1/cafes/{cafe_id}")
    assert get_response.status_code == 404

@pytest.mark.anyio
async def test_search_cafes(client: AsyncClient):
    await client.post("/api/v1/cafes/", json=cafe_data)
    
    response = await client.get("/api/v1/cafes/search/Test")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "Test" in data[0]["name"]

@pytest.mark.anyio
async def test_find_nearby_cafes(client: AsyncClient):
    await client.post("/api/v1/cafes/", json=cafe_data)

    # Coordinates close to the test cafe
    lon, lat = -73.986, 40.748
    response = await client.get(f"/api/v1/cafes/nearby/?longitude={lon}&latitude={lat}&max_distance=1000")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == "Test Cafe"

@pytest.mark.anyio
async def test_find_cafes_by_amenities(client: AsyncClient):
    await client.post("/api/v1/cafes/", json=cafe_data)

    response = await client.get("/api/v1/cafes/by-amenities/?amenities=wifi&amenities=power_outlets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "wifi" in data[0]["amenities"]
    assert "power_outlets" in data[0]["amenities"]

@pytest.mark.anyio
async def test_find_cafes_by_rating(client: AsyncClient):
    await client.post("/api/v1/cafes/", json=cafe_data)

    response = await client.get("/api/v1/cafes/by-rating/?min_rating=4")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["average_rating"] >= 4 