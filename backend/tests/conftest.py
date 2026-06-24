"""Shared test fixtures for all test files."""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import engine, Base, async_session


def unique_email():
    import uuid
    return f"user_{uuid.uuid4().hex[:8]}@test.ee"


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Create tables and seed data before each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as db:
        from app.services.seed import seed_database
        await seed_database(db)
        await db.commit()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(setup_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient):
    """Create a user and return auth headers."""
    import uuid
    email = f"auth_{uuid.uuid4().hex[:8]}@test.ee"
    password = "testpass123"

    # Register
    reg_resp = await client.post("/api/auth/register", json={
        "email": email, "password": password, "display_name": "Test User"
    })

    # Login
    login_resp = await client.post("/api/auth/login", json={
        "email": email, "password": password
    })
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
