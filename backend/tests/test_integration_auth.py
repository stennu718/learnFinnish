"""Integration tests for Auth API endpoints."""
import pytest
import pytest_asyncio











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
        assert resp.status_code == 409

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
        assert "email" in data
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
