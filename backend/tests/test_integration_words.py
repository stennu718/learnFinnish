"""Integration tests for Word Pairs & Progress API endpoints."""
import pytest
import pytest_asyncio











class TestWordEndpoints:
    """Test word pairs API endpoints."""

    @pytest.mark.asyncio
    async def test_list_words(self, client, auth_headers):
        resp = await client.get("/api/words", headers=auth_headers)
        assert resp.status_code == 200
        words = resp.json()
        assert len(words) > 0

    @pytest.mark.asyncio
    async def test_list_words_pagination(self, client, auth_headers):
        resp = await client.get("/api/words?limit=10&offset=0", headers=auth_headers)
        assert resp.status_code == 200
        words = resp.json()
        assert len(words) <= 10

    @pytest.mark.asyncio
    async def test_list_words_by_category(self, client, auth_headers):
        resp = await client.get("/api/words?category=greetings", headers=auth_headers)
        assert resp.status_code == 200
        words = resp.json()
        for w in words:
            assert w["category"] == "greetings"

    @pytest.mark.asyncio
    async def test_list_words_cognates_only(self, client, auth_headers):
        resp = await client.get("/api/words?cognates_only=true", headers=auth_headers)
        assert resp.status_code == 200
        words = resp.json()
        for w in words:
            assert w["is_cognate"] is True

    @pytest.mark.asyncio
    async def test_list_categories(self, client, auth_headers):
        resp = await client.get("/api/words/categories", headers=auth_headers)
        assert resp.status_code == 200
        categories = resp.json()
        assert len(categories) > 0
        assert "greetings" in categories

    @pytest.mark.asyncio
    async def test_words_unauthenticated(self, client):
        resp = await client.get("/api/words")
        assert resp.status_code == 401


class TestProgressEndpoints:
    """Test progress API endpoints."""

    @pytest.mark.asyncio
    async def test_progress_initial(self, client, auth_headers):
        resp = await client.get("/api/progress", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "xp" in data
        assert "level" in data
        assert "total_reviews" in data
        assert "correct_reviews" in data
        assert "accuracy" in data
        assert "current_streak" in data
        assert "longest_streak" in data

    @pytest.mark.asyncio
    async def test_progress_after_review(self, client, auth_headers):
        # Init and review
        await client.post("/api/srs/init", headers=auth_headers)
        resp = await client.get("/api/srs/due", headers=auth_headers)
        cards = resp.json()
        if cards:
            await client.post("/api/srs/review", headers=auth_headers, json={
                "card_id": cards[0]["card_id"],
                "quality": 4,
            })

        resp = await client.get("/api/progress", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_reviews"] >= 0

    @pytest.mark.asyncio
    async def test_progress_unauthenticated(self, client):
        resp = await client.get("/api/progress")
        assert resp.status_code == 401
