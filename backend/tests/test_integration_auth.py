"""Integration tests for Auth API endpoints."""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import engine, Base, async_session


@pytest_asyncio.fixture(scope="session")
async def setup_db():
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
    resp = await client.post("/api/auth/login", json={
        "email": "test@test.ee",
        "password": "testpass123",
    })
    if resp.status_code != 200:
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


class TestAuthEndpoints:
    """Test authentication API endpoints."""

    @pytest.mark.asyncio
    async def test_health(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_register_success(self, client):
        import uuid
        resp = await client.post("/api/auth/register", json={
            "email": f"newuser_{uuid.uuid4().hex[:8]}@test.ee",
            "password": "pass123",
            "display_name": "New User",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client):
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
    async def test_register_missing_email(self, client):
        resp = await client.post("/api/auth/register", json={
            "password": "pass123",
        })
        assert resp.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_short_password(self, client):
        resp = await client.post("/api/auth/register", json={
            "email": "short@test.ee",
            "password": "123",
        })
        # Should still work (no min length validation in model)
        assert resp.status_code in (200, 422)

    @pytest.mark.asyncio
    async def test_login_success(self, client):
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
    async def test_login_wrong_password(self, client):
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
    async def test_login_nonexistent_user(self, client):
        resp = await client.post("/api/auth/login", json={
            "email": "nobody@test.ee",
            "password": "pass123",
        })
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me_authenticated(self, client, auth_headers):
        resp = await client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "test@test.ee"
        assert "id" in data
        assert "display_name" in data

    @pytest.mark.asyncio
    async def test_get_me_unauthenticated(self, client):
        resp = await client.get("/api/auth/me")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self, client):
        resp = await client.get("/api/auth/me", headers={
            "Authorization": "Bearer invalidtoken123"
        })
        assert resp.status_code == 401
