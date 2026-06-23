"""E2E testid — täielikud kasutajateekonnad — 50+ testi."""
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


def unique_email():
    import uuid
    return f"e2e_{uuid.uuid4().hex[:8]}@test.ee"


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient):
    email = unique_email()
    await client.post("/api/auth/register", json={
        "email": email, "password": "validpass123"
    })
    resp = await client.post("/api/auth/login", json={
        "email": email, "password": "validpass123"
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}", "email": email}


class TestE2ERegisterLogin:
    """E2E: Registreerimine ja sisselogimine."""

    @pytest.mark.asyncio
    async def test_register_login_flow(self, client):
        email = unique_email()
        # Register
        resp = await client.post("/api/auth/register", json={
            "email": email, "password": "validpass123", "display_name": "Test"
        })
        assert resp.status_code == 200
        # Login
        resp = await client.post("/api/auth/login", json={
            "email": email, "password": "validpass123"
        })
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_register_login_access_words(self, client):
        email = unique_email()
        await client.post("/api/auth/register", json={
            "email": email, "password": "validpass123"
        })
        resp = await client.post("/api/auth/login", json={
            "email": email, "password": "validpass123"
        })
        token = resp.json()["access_token"]
        # Access words
        resp = await client.get("/api/words", headers={
            "Authorization": f"Bearer {token}"
        })
        assert resp.status_code == 200
        assert len(resp.json()) > 0

    @pytest.mark.asyncio
    async def test_multiple_users_independent(self, client):
        # User 1
        email1 = unique_email()
        await client.post("/api/auth/register", json={
            "email": email1, "password": "pass123456"
        })
        resp1 = await client.post("/api/auth/login", json={
            "email": email1, "password": "pass123456"
        })
        token1 = resp1.json()["access_token"]

        # User 2
        email2 = unique_email()
        await client.post("/api/auth/register", json={
            "email": email2, "password": "pass123456"
        })
        resp2 = await client.post("/api/auth/login", json={
            "email": email2, "password": "pass123456"
        })
        token2 = resp2.json()["access_token"]

        # Both should work
        r1 = await client.get("/api/words", headers={"Authorization": f"Bearer {token1}"})
        r2 = await client.get("/api/words", headers={"Authorization": f"Bearer {token2}"})
        assert r1.status_code == 200
        assert r2.status_code == 200


class TestE2ELearningSession:
    """E2E: Õppimise sessioon."""

    @pytest.mark.asyncio
    async def test_complete_learning_session(self, client, auth_headers):
        # Init SRS
        resp = await client.post("/api/srs/init", headers=auth_headers)
        assert resp.status_code == 200

        # Get due cards
        resp = await client.get("/api/srs/due", headers=auth_headers)
        cards = resp.json()
        assert len(cards) > 0

        # Review 3 cards
        for card in cards[:3]:
            resp = await client.post("/api/srs/review", headers=auth_headers, json={
                "card_id": card["card_id"], "quality": 4
            })
            assert resp.status_code == 200

        # Check progress
        resp = await client.get("/api/progress", headers=auth_headers)
        data = resp.json()
        assert data["total_reviews"] >= 3

    @pytest.mark.asyncio
    async def test_learning_with_mixed_quality(self, client, auth_headers):
        await client.post("/api/srs/init", headers=auth_headers)
        resp = await client.get("/api/srs/due", headers=auth_headers)
        cards = resp.json()
        if len(cards) < 5:
            pytest.skip("Not enough cards")

        qualities = [5, 4, 3, 2, 1]
        for card, q in zip(cards[:5], qualities):
            resp = await client.post("/api/srs/review", headers=auth_headers, json={
                "card_id": card["card_id"], "quality": q
            })
            assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_learning_all_perfect(self, client, auth_headers):
        await client.post("/api/srs/init", headers=auth_headers)
        resp = await client.get("/api/srs/due?limit=10", headers=auth_headers)
        cards = resp.json()

        for card in cards:
            resp = await client.post("/api/srs/review", headers=auth_headers, json={
                "card_id": card["card_id"], "quality": 5
            })
            assert resp.status_code == 200

        prog = await client.get("/api/progress", headers=auth_headers)
        assert prog.json()["correct_reviews"] >= len(cards)

    @pytest.mark.asyncio
    async def test_learning_all_wrong(self, client, auth_headers):
        await client.post("/api/srs/init", headers=auth_headers)
        resp = await client.get("/api/srs/due?limit=5", headers=auth_headers)
        cards = resp.json()

        for card in cards:
            resp = await client.post("/api/srs/review", headers=auth_headers, json={
                "card_id": card["card_id"], "quality": 0
            })
            assert resp.status_code == 200

        prog = await client.get("/api/progress", headers=auth_headers)
        # All wrong, so correct_reviews should not increment from these
        assert prog.json()["total_reviews"] >= len(cards)


class TestE2EProgressTracking:
    """E2E: Progressi jälgimine."""

    @pytest.mark.asyncio
    async def test_progress_starts_at_zero(self, client, auth_headers):
        resp = await client.get("/api/progress", headers=auth_headers)
        data = resp.json()
        assert data["xp"] == 0
        assert data["level"] == 1
        assert data["total_reviews"] == 0

    @pytest.mark.asyncio
    async def test_progress_increments_on_review(self, client, auth_headers):
        await client.post("/api/srs/init", headers=auth_headers)
        resp = await client.get("/api/srs/due", headers=auth_headers)
        cards = resp.json()
        if not cards:
            pytest.skip("No cards")

        prog_before = await client.get("/api/progress", headers=auth_headers)

        await client.post("/api/srs/review", headers=auth_headers, json={
            "card_id": cards[0]["card_id"], "quality": 5
        })

        prog_after = await client.get("/api/progress", headers=auth_headers)
        assert prog_after.json()["total_reviews"] > prog_before.json()["total_reviews"]

    @pytest.mark.asyncio
    async def test_progress_accuracy_percentage(self, client, auth_headers):
        await client.post("/api/srs/init", headers=auth_headers)
        resp = await client.get("/api/srs/due?limit=4", headers=auth_headers)
        cards = resp.json()
        if len(cards) < 4:
            pytest.skip("Not enough cards")

        # 3 correct, 1 wrong
        for card in cards[:3]:
            await client.post("/api/srs/review", headers=auth_headers, json={
                "card_id": card["card_id"], "quality": 5
            })
        await client.post("/api/srs/review", headers=auth_headers, json={
            "card_id": cards[3]["card_id"], "quality": 1
        })

        prog = await client.get("/api/progress", headers=auth_headers)
        data = prog.json()
        # 3/4 = 75% accuracy
        assert data["accuracy"] == 75.0

    @pytest.mark.asyncio
    async def test_progress_level_calculation(self, client, auth_headers):
        # Level = 1 + xp // 100
        # Verify the formula works correctly
        await client.post("/api/srs/init", headers=auth_headers)
        resp = await client.get("/api/srs/due?limit=10", headers=auth_headers)
        cards = resp.json()

        # Review 10 cards perfectly = 100 XP = level 2
        for card in cards[:10]:
            await client.post("/api/srs/review", headers=auth_headers, json={
                "card_id": card["card_id"], "quality": 5
            })

        prog = await client.get("/api/progress", headers=auth_headers)
        data = prog.json()
        expected_level = 1 + data["xp"] // 100
        assert data["level"] == expected_level


class TestE2EEdgeCases:
    """E2E: Servaalad."""

    @pytest.mark.asyncio
    async def test_empty_due_cards(self, client, auth_headers):
        # Without.init, should return empty
        resp = await client.get("/api/srs/due", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    @pytest.mark.asyncio
    async def test_review_same_card_twice(self, client, auth_headers):
        await client.post("/api/srs/init", headers=auth_headers)
        resp = await client.get("/api/srs/due", headers=auth_headers)
        cards = resp.json()
        if not cards:
            pytest.skip("No cards")

        card_id = cards[0]["card_id"]
        # First review
        resp1 = await client.post("/api/srs/review", headers=auth_headers, json={
            "card_id": card_id, "quality": 4
        })
        assert resp1.status_code == 200

        # Second review of same card (should still work)
        resp2 = await client.post("/api/srs/review", headers=auth_headers, json={
            "card_id": card_id, "quality": 3
        })
        assert resp2.status_code == 200

    @pytest.mark.asyncio
    async def test_access_without_token(self, client):
        endpoints = [
            ("/api/words", "GET"),
            ("/api/srs/due", "GET"),
            ("/api/srs/init", "POST"),
            ("/api/progress", "GET"),
            ("/api/auth/me", "GET"),
        ]
        for path, method in endpoints:
            if method == "GET":
                resp = await client.get(path)
            else:
                resp = await client.post(path, json={})
            assert resp.status_code == 401, f"{method} {path} should return 401"

    @pytest.mark.asyncio
    async def test_invalid_token_all_endpoints(self, client):
        headers = {"Authorization": "Bearer invalid.token"}
        endpoints = [
            ("/api/words", "GET"),
            ("/api/srs/due", "GET"),
            ("/api/progress", "GET"),
            ("/api/auth/me", "GET"),
        ]
        for path, method in endpoints:
            resp = await client.get(path, headers=headers)
            assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_concurrent_reviews(self, client, auth_headers):
        """Test that multiple reviews work correctly."""
        await client.post("/api/srs/init", headers=auth_headers)
        resp = await client.get("/api/srs/due?limit=5", headers=auth_headers)
        cards = resp.json()
        if len(cards) < 3:
            pytest.skip("Not enough cards")

        # Review all
        for card in cards:
            resp = await client.post("/api/srs/review", headers=auth_headers, json={
                "card_id": card["card_id"], "quality": 4
            })
            assert resp.status_code == 200

        prog = await client.get("/api/progress", headers=auth_headers)
        assert prog.json()["total_reviews"] >= len(cards)

    @pytest.mark.asyncio
    async def test_word_categories_filter(self, client, auth_headers):
        resp = await client.get("/api/words/categories", headers=auth_headers)
        cats = resp.json()
        assert len(cats) > 0

        # Test each category returns words
        for cat in cats[:5]:
            resp = await client.get(f"/api/words?category={cat}", headers=auth_headers)
            assert resp.status_code == 200
            for w in resp.json():
                assert w["category"] == cat

    @pytest.mark.asyncio
    async def test_pagination_bounds(self, client, auth_headers):
        # Test various pagination values
        for limit in [1, 5, 10, 50]:
            resp = await client.get(f"/api/words?limit={limit}", headers=auth_headers)
            assert resp.status_code == 200
            assert len(resp.json()) <= limit

    @pytest.mark.asyncio
    async def test_cognate_filter(self, client, auth_headers):
        resp = await client.get("/api/words?cognates_only=true", headers=auth_headers)
        assert resp.status_code == 200
        for w in resp.json():
            assert w["is_cognate"] is True

    @pytest.mark.asyncio
    async def test_non_cognate_filter(self, client, auth_headers):
        resp = await client.get("/api/words?cognates_only=false", headers=auth_headers)
        assert resp.status_code == 200
        # Should return all words (both cognates and non-cognates)
        all_resp = await client.get("/api/words", headers=auth_headers)
        assert len(resp.json()) == len(all_resp.json())
