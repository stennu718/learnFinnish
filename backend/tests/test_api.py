"""Tests for learnFinnish backend — legacy tests."""
import pytest


class TestHealth:
    @pytest.mark.asyncio
    async def test_health(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestAuth:
    @pytest.mark.asyncio
    async def test_register(self, client):
        import uuid
        email = f"newuser_{uuid.uuid4().hex[:8]}@test.ee"
        resp = await client.post("/api/auth/register", json={
            "email": email, "password": "pass123", "display_name": "New"
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client):
        import uuid
        email = f"dup_{uuid.uuid4().hex[:8]}@test.ee"
        await client.post("/api/auth/register", json={
            "email": email, "password": "pass123"
        })
        resp = await client.post("/api/auth/register", json={
            "email": email, "password": "pass123"
        })
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_login(self, client):
        import uuid
        email = f"login_{uuid.uuid4().hex[:8]}@test.ee"
        await client.post("/api/auth/register", json={
            "email": email, "password": "mypass"
        })
        resp = await client.post("/api/auth/login", json={
            "email": email, "password": "mypass"
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client):
        import uuid
        email = f"wrong_{uuid.uuid4().hex[:8]}@test.ee"
        await client.post("/api/auth/register", json={
            "email": email, "password": "rightpass"
        })
        resp = await client.post("/api/auth/login", json={
            "email": email, "password": "wrongpass"
        })
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me(self, client, auth_headers):
        resp = await client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200


class TestSRS:
    @pytest.mark.asyncio
    async def test_srs_review_flow(self, client, auth_headers):
        resp = await client.post("/api/srs/init", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["created"] >= 0

        resp = await client.get("/api/srs/due", headers=auth_headers)
        assert resp.status_code == 200
        cards = resp.json()
        assert len(cards) >= 0

        if cards:
            card_id = cards[0]["card_id"]
            resp = await client.post("/api/srs/review", headers=auth_headers, json={
                "card_id": card_id, "quality": 4
            })
            assert resp.status_code == 200
            assert resp.json()["xp_earned"] > 0


class TestProgress:
    @pytest.mark.asyncio
    async def test_progress(self, client, auth_headers):
        resp = await client.get("/api/progress", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "xp" in data
        assert "level" in data
