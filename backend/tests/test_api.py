"""Tests for learnFinnish backend."""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import engine, Base, async_session


@pytest_asyncio.fixture(scope="session")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Seed word pairs
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
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient):
    # Login (user already created by test_register, or create fresh)
    resp = await client.post("/api/auth/login", json={
        "email": "test@test.ee",
        "password": "testpass123",
    })
    if resp.status_code != 200:
        # Register first
        await client.post("/api/auth/register", json={
            "email": "test@test.ee",
            "password": "testpass123",
            "display_name": "Test User",
        })
        resp = await client.post("/api/auth/login", json={
            "email": "test@test.ee",
            "password": "testpass123",
        })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    resp = await client.post("/api/auth/register", json={
        "email": "newuser@test.ee",
        "password": "pass123",
        "display_name": "New",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "email": "dup@test.ee",
        "password": "pass123",
    })
    resp = await client.post("/api/auth/register", json={
        "email": "dup@test.ee",
        "password": "pass123",
    })
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "email": "login@test.ee",
        "password": "mypass",
    })
    resp = await client.post("/api/auth/login", json={
        "email": "login@test.ee",
        "password": "mypass",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "email": "wrong@test.ee",
        "password": "rightpass",
    })
    resp = await client.post("/api/auth/login", json={
        "email": "wrong@test.ee",
        "password": "wrongpass",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@test.ee"


@pytest.mark.asyncio
async def test_srs_review_flow(client: AsyncClient, auth_headers: dict):
    # Init cards
    resp = await client.post("/api/srs/init", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["created"] > 0

    # Get due cards
    resp = await client.get("/api/srs/due", headers=auth_headers)
    assert resp.status_code == 200
    cards = resp.json()
    assert len(cards) > 0

    # Review a card
    card_id = cards[0]["card_id"]
    resp = await client.post("/api/srs/review", headers=auth_headers, json={
        "card_id": card_id,
        "quality": 4,
    })
    assert resp.status_code == 200
    assert resp.json()["xp_earned"] > 0


@pytest.mark.asyncio
async def test_progress(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/progress", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "xp" in data
    assert "level" in data
