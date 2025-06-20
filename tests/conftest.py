import pytest
from httpx import AsyncClient
from app.main import app
from app.config.database import Database

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    await Database.connect_db(test_mode=True)
    yield
    await Database.close_db() 