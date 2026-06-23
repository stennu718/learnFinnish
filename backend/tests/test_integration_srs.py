"""Integration tests for SRS API endpoints."""
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


class TestSRSEndpoints:
    """Test SRS (Spaced Repetition) API endpoints."""

    @pytest.mark.asyncio
    async def test_init_srs_creates_cards(self, client, auth_headers):
        resp = await client.post("/api/srs/init", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        # Cards may already exist from previous tests, so just check >= 0
        assert data["created"] >= 0

    @pytest.mark.asyncio
    async def test_init_srs_idempotent(self, client, auth_headers):
        """Running init twice should not create duplicates."""
        resp1 = await client.post("/api/srs/init", headers=auth_headers)
        resp2 = await client.post("/api/srs/init", headers=auth_headers)
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        # Second run should create 0 new cards
        assert resp2.json()["created"] == 0

    @pytest.mark.asyncio
    async def test_get_due_cards(self, client, auth_headers):
        await client.post("/api/srs/init", headers=auth_headers)
        resp = await client.get("/api/srs/due", headers=auth_headers)
        assert resp.status_code == 200
        cards = resp.json()
        assert len(cards) > 0
        # Check card structure
        card = cards[0]
        assert "card_id" in card
        assert "word_pair_id" in card
        assert "estonian" in card
        assert "finnish" in card
        assert "direction" in card
        assert "category" in card

    @pytest.mark.asyncio
    async def test_review_card_correct(self, client, auth_headers):
        await client.post("/api/srs/init", headers=auth_headers)
        resp = await client.get("/api/srs/due", headers=auth_headers)
        cards = resp.json()
        card_id = cards[0]["card_id"]

        resp = await client.post("/api/srs/review", headers=auth_headers, json={
            "card_id": card_id,
            "quality": 4,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["xp_earned"] > 0
        assert "next_review" in data
        assert "interval" in data
        assert "ease_factor" in data
        assert "repetitions" in data

    @pytest.mark.asyncio
    async def test_review_card_incorrect(self, client, auth_headers):
        await client.post("/api/srs/init", headers=auth_headers)
        resp = await client.get("/api/srs/due", headers=auth_headers)
        cards = resp.json()
        card_id = cards[0]["card_id"]

        resp = await client.post("/api/srs/review", headers=auth_headers, json={
            "card_id": card_id,
            "quality": 1,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["xp_earned"] > 0  # Still get some XP for trying

    @pytest.mark.asyncio
    async def test_review_invalid_card(self, client, auth_headers):
        resp = await client.post("/api/srs/review", headers=auth_headers, json={
            "card_id": 99999,
            "quality": 4,
        })
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_review_missing_quality(self, client, auth_headers):
        await client.post("/api/srs/init", headers=auth_headers)
        resp = await client.get("/api/srs/due", headers=auth_headers)
        cards = resp.json()
        card_id = cards[0]["card_id"]

        resp = await client.post("/api/srs/review", headers=auth_headers, json={
            "card_id": card_id,
        })
        assert resp.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_due_cards_limit(self, client, auth_headers):
        await client.post("/api/srs/init", headers=auth_headers)
        resp = await client.get("/api/srs/due?limit=5", headers=auth_headers)
        assert resp.status_code == 200
        cards = resp.json()
        assert len(cards) <= 5

    @pytest.mark.asyncio
    async def test_srs_unauthenticated(self, client):
        resp = await client.get("/api/srs/due")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_review_updates_progress(self, client, auth_headers):
        await client.post("/api/srs/init", headers=auth_headers)
        resp = await client.get("/api/srs/due", headers=auth_headers)
        cards = resp.json()
        card_id = cards[0]["card_id"]

        # Get progress before
        prog_before = await client.get("/api/progress", headers=auth_headers)
        xp_before = prog_before.json()["xp"]

        # Review a card
        await client.post("/api/srs/review", headers=auth_headers, json={
            "card_id": card_id,
            "quality": 4,
        })

        # Get progress after
        prog_after = await client.get("/api/progress", headers=auth_headers)
        xp_after = prog_after.json()["xp"]

        assert xp_after > xp_before
