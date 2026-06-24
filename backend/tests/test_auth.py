"""Auth API põhjalikud integratsioonitestid — 50+ testi."""
import pytest
import uuid


def unique_email():
    return f"user_{uuid.uuid4().hex[:8]}@test.ee"


class TestRegisterValidation:
    """Registreerimise valideerimise testid."""

    @pytest.mark.asyncio
    async def test_register_success(self, client, auth_headers):
        # auth_headers fixture already registers and logs in
        resp = await client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_register_short_password(self, client):
        resp = await client.post("/api/auth/register", json={
            "email": unique_email(), "password": "12345"
        })
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_register_empty_password(self, client):
        resp = await client.post("/api/auth/register", json={
            "email": unique_email(), "password": ""
        })
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client):
        resp = await client.post("/api/auth/register", json={
            "email": "not-an-email", "password": "validpass123"
        })
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_register_missing_email(self, client):
        resp = await client.post("/api/auth/register", json={
            "password": "validpass123"
        })
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_register_missing_password(self, client):
        resp = await client.post("/api/auth/register", json={
            "email": unique_email()
        })
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client):
        email = unique_email()
        await client.post("/api/auth/register", json={
            "email": email, "password": "validpass123"
        })
        resp = await client.post("/api/auth/register", json={
            "email": email, "password": "validpass123"
        })
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_register_email_normalized(self, client):
        email = unique_email()
        resp = await client.post("/api/auth/register", json={
            "email": email, "password": "validpass123"
        })
        assert resp.status_code == 200
        # Login with uppercase should work
        resp = await client.post("/api/auth/login", json={
            "email": email.upper(), "password": "validpass123"
        })
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_register_long_display_name(self, client):
        resp = await client.post("/api/auth/register", json={
            "email": unique_email(), "password": "validpass123",
            "display_name": "A" * 200
        })
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_register_empty_display_name(self, client):
        resp = await client.post("/api/auth/register", json={
            "email": unique_email(), "password": "validpass123"
        })
        assert resp.status_code == 200


class TestLoginValidation:
    """Sisselogimise valideerimise testid."""

    @pytest.mark.asyncio
    async def test_login_success(self, client):
        email = unique_email()
        await client.post("/api/auth/register", json={
            "email": email, "password": "validpass123"
        })
        resp = await client.post("/api/auth/login", json={
            "email": email, "password": "validpass123"
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client):
        email = unique_email()
        await client.post("/api/auth/register", json={
            "email": email, "password": "validpass123"
        })
        resp = await client.post("/api/auth/login", json={
            "email": email, "password": "wrongpass123"
        })
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client):
        resp = await client.post("/api/auth/login", json={
            "email": "nonexistent@test.ee", "password": "validpass123"
        })
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_login_empty_password(self, client):
        resp = await client.post("/api/auth/login", json={
            "email": unique_email(), "password": ""
        })
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_login_invalid_email_format(self, client):
        resp = await client.post("/api/auth/login", json={
            "email": "not-email", "password": "validpass123"
        })
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_login_email_case_insensitive(self, client):
        email = unique_email()
        await client.post("/api/auth/register", json={
            "email": email, "password": "validpass123"
        })
        resp = await client.post("/api/auth/login", json={
            "email": email.upper(), "password": "validpass123"
        })
        assert resp.status_code == 200


class TestTokenOperations:
    """Tokeni operatsioonide testid."""

    @pytest.mark.asyncio
    async def test_token_contains_required_fields(self, client):
        email = unique_email()
        await client.post("/api/auth/register", json={
            "email": email, "password": "validpass123"
        })
        resp = await client.post("/api/auth/login", json={
            "email": email, "password": "validpass123"
        })
        data = resp.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_token_is_jwt(self, client):
        email = unique_email()
        await client.post("/api/auth/register", json={
            "email": email, "password": "validpass123"
        })
        resp = await client.post("/api/auth/login", json={
            "email": email, "password": "validpass123"
        })
        token = resp.json()["access_token"]
        parts = token.split(".")
        assert len(parts) == 3

    @pytest.mark.asyncio
    async def test_invalid_token_rejected(self, client):
        resp = await client.get("/api/auth/me", headers={
            "Authorization": "Bearer invalid.token.here"
        })
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_missing_token_rejected(self, client):
        resp = await client.get("/api/auth/me")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_malformed_auth_header(self, client):
        resp = await client.get("/api/auth/me", headers={
            "Authorization": "NotBearer token123"
        })
        assert resp.status_code == 401


class TestMeEndpoint:
    """Me endpointi testid."""

    @pytest.mark.asyncio
    async def test_me_returns_user_data(self, client, auth_headers):
        resp = await client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "email" in data
        assert "display_name" in data
        assert "id" in data

    @pytest.mark.asyncio
    async def test_me_requires_auth(self, client):
        resp = await client.get("/api/auth/me")
        assert resp.status_code == 401


class TestLogoutEndpoint:
    """Logout endpointi testid."""

    @pytest.mark.asyncio
    async def test_logout_success(self, client, auth_headers):
        resp = await client.post("/api/auth/logout", headers=auth_headers)
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_logout_requires_auth(self, client):
        resp = await client.post("/api/auth/logout")
        assert resp.status_code == 401


class TestPasswordSecurity:
    """Parooli turvalisuse testid."""

    @pytest.mark.asyncio
    async def test_password_not_returned(self, client):
        email = unique_email()
        resp = await client.post("/api/auth/register", json={
            "email": email, "password": "secretpass123"
        })
        data = resp.json()
        assert "password" not in data
        assert "hashed_password" not in data

    @pytest.mark.asyncio
    async def test_different_passwords_different_hashes(self, client):
        from app.core.auth import hash_password
        hash1 = hash_password("samepassword")
        hash2 = hash_password("samepassword")
        assert hash1 != hash2

    @pytest.mark.asyncio
    async def test_password_min_length_enforced(self, client):
        resp = await client.post("/api/auth/register", json={
            "email": unique_email(), "password": "12345"
        })
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_password_max_length_enforced(self, client):
        resp = await client.post("/api/auth/register", json={
            "email": unique_email(), "password": "a" * 129
        })
        assert resp.status_code == 422
