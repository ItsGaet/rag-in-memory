import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

from app.main import app
from app.core.db import Base, get_async_db

# --- Test Database Setup ---
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

async_engine = create_async_engine(TEST_DATABASE_URL)
AsyncTestingSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

# --- Dependency Override ---
async def override_get_async_db():
    async with AsyncTestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_async_db] = override_get_async_db

# --- Pytest Fixtures ---
@pytest.fixture(scope="function")
async def async_client() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    # Create tables for every test
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Drop tables after every test
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    # Cleanup the test db file
    if os.path.exists("./test.db"):
        os.remove("./test.db")

# --- Tests ---
@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
