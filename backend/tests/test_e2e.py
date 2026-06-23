"""E2E tests — full user journey from registration to learning."""
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


class TestE2EUserJourney:
    """End-to-end test: register → login → learn → review → check progress."""

    @pytest.mark.asyncio
    async def test_complete_learning_session(self, client):
        """Full user journey: register, init SRS, review cards, check progress."""

        # Step 1: Register
        email = f"e2e_{id(self)}@test.ee"
        resp = await client.post("/api/auth/register", json={
            "email": email,
            "password": "e2epass123",
            "display_name": "E2E User",
        })
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 2: Verify profile
        resp = await client.get("/api/auth/me", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == email

        # Step 3: Check initial progress
        resp = await client.get("/api/progress", headers=headers)
        assert resp.status_code == 200
        initial_xp = resp.json()["xp"]
        assert initial_xp == 0

        # Step 4: Initialize SRS cards
        resp = await client.post("/api/srs/init", headers=headers)
        assert resp.status_code == 200
        cards_created = resp.json()["created"]
        assert cards_created > 0

        # Step 5: Get due cards
        resp = await client.get("/api/srs/due?limit=5", headers=headers)
        assert resp.status_code == 200
        cards = resp.json()
        assert len(cards) > 0

        # Step 6: Review 3 cards
        for i, card in enumerate(cards[:3]):
            resp = await client.post("/api/srs/review", headers=headers, json={
                "card_id": card["card_id"],
                "quality": 4,
            })
            assert resp.status_code == 200
            assert resp.json()["xp_earned"] > 0

        # Step 7: Check updated progress
        resp = await client.get("/api/progress", headers=headers)
        assert resp.status_code == 200
        final_data = resp.json()
        assert final_data["xp"] > initial_xp
        assert final_data["total_reviews"] >= 3
        assert final_data["level"] >= 1

        # Step 8: List words
        resp = await client.get("/api/words?limit=10", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) > 0

        # Step 9: List categories
        resp = await client.get("/api/words/categories", headers=headers)
        assert resp.status_code == 200
        categories = resp.json()
        assert len(categories) > 0

    @pytest.mark.asyncio
    async def test_multiple_review_sessions(self, client):
        """Test that multiple review sessions work correctly."""

        # Register
        email = f"multi_{id(self)}@test.ee"
        resp = await client.post("/api/auth/register", json={
            "email": email,
            "password": "multipass123",
        })
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Init SRS
        await client.post("/api/srs/init", headers=headers)

        # Session 1: Review some cards
        resp = await client.get("/api/srs/due?limit=3", headers=headers)
        cards = resp.json()
        for card in cards:
            await client.post("/api/srs/review", headers=headers, json={
                "card_id": card["card_id"],
                "quality": 4,
            })

        # Check progress
        resp = await client.get("/api/progress", headers=headers)
        xp_after_session1 = resp.json()["xp"]

        # Session 2: Review more cards
        resp = await client.get("/api/srs/due?limit=3", headers=headers)
        cards = resp.json()
        for card in cards:
            await client.post("/api/srs/review", headers=headers, json={
                "card_id": card["card_id"],
                "quality": 3,
            })

        # Check progress increased
        resp = await client.get("/api/progress", headers=headers)
        xp_after_session2 = resp.json()["xp"]
        assert xp_after_session2 >= xp_after_session1

    @pytest.mark.asyncio
    async def test_error_handling(self, client):
        """Test error handling for various edge cases."""

        # Register
        email = f"error_{id(self)}@test.ee"
        resp = await client.post("/api/auth/register", json={
            "email": email,
            "password": "errorpass123",
        })
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to review non-existent card
        resp = await client.post("/api/srs/review", headers=headers, json={
            "card_id": 999999,
            "quality": 4,
        })
        assert resp.status_code == 404

        # Try to access without auth
        resp = await client.get("/api/srs/due")
        assert resp.status_code == 401

        # Try with invalid token
        resp = await client.get("/api/srs/due", headers={
            "Authorization": "Bearer invalid_token"
        })
        assert resp.status_code == 401

        # Try invalid quality value
        await client.post("/api/srs/init", headers=headers)
        resp = await client.get("/api/srs/due", headers=headers)
        cards = resp.json()
        if cards:
            resp = await client.post("/api/srs/review", headers=headers, json={
                "card_id": cards[0]["card_id"],
                "quality": 99,  # Invalid quality
            })
            # Should either reject or clamp
            assert resp.status_code in (200, 422)
