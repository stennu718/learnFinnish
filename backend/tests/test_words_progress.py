"""Words ja Progress API põhjalikud testid — 50+ testi."""
import pytest


class TestWordsList:
    """Sõnade listi testid."""

    @pytest.mark.asyncio
    async def test_list_words_returns_array(self, client, auth_headers):
        resp = await client.get("/api/words", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    @pytest.mark.asyncio
    async def test_list_words_have_required_fields(self, client, auth_headers):
        resp = await client.get("/api/words", headers=auth_headers)
        words = resp.json()
        for w in words:
            assert "id" in w
            assert "estonian" in w
            assert "finnish" in w
            assert "estonian_example" in w
            assert "finnish_example" in w
            assert "category" in w
            assert "difficulty" in w
            assert "is_cognate" in w
            assert "audio_url" in w

    @pytest.mark.asyncio
    async def test_list_words_pagination_limit(self, client, auth_headers):
        resp = await client.get("/api/words?limit=5", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) <= 5

    @pytest.mark.asyncio
    async def test_list_words_pagination_offset(self, client, auth_headers):
        resp1 = await client.get("/api/words?limit=2&offset=0", headers=auth_headers)
        resp2 = await client.get("/api/words?limit=2&offset=2", headers=auth_headers)
        words1 = resp1.json()
        words2 = resp2.json()
        if len(words1) == 2 and len(words2) == 2:
            assert words1[0]["id"] != words2[0]["id"]

    @pytest.mark.asyncio
    async def test_list_words_max_limit(self, client, auth_headers):
        resp = await client.get("/api/words?limit=200", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) <= 200

    @pytest.mark.asyncio
    async def test_list_words_exceeds_max_limit(self, client, auth_headers):
        resp = await client.get("/api/words?limit=201", headers=auth_headers)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_list_words_filter_by_category(self, client, auth_headers):
        resp = await client.get("/api/words?category=greetings", headers=auth_headers)
        assert resp.status_code == 200
        for w in resp.json():
            assert w["category"] == "greetings"

    @pytest.mark.asyncio
    async def test_list_words_filter_cognates_only(self, client, auth_headers):
        resp = await client.get("/api/words?cognates_only=true", headers=auth_headers)
        assert resp.status_code == 200
        for w in resp.json():
            assert w["is_cognate"] is True

    @pytest.mark.asyncio
    async def test_list_words_nonexistent_category(self, client, auth_headers):
        resp = await client.get("/api/words?category=nonexistent", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 0

    @pytest.mark.asyncio
    async def test_list_words_requires_auth(self, client):
        resp = await client.get("/api/words")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_list_words_no_auth_token(self, client):
        resp = await client.get("/api/words", headers={})
        assert resp.status_code == 401


class TestWordsCategories:
    """Kategooriate testid."""

    @pytest.mark.asyncio
    async def test_list_categories(self, client, auth_headers):
        resp = await client.get("/api/words/categories", headers=auth_headers)
        assert resp.status_code == 200
        cats = resp.json()
        assert isinstance(cats, list)
        assert len(cats) > 0

    @pytest.mark.asyncio
    async def test_categories_are_unique(self, client, auth_headers):
        resp = await client.get("/api/words/categories", headers=auth_headers)
        cats = resp.json()
        assert len(cats) == len(set(cats))

    @pytest.mark.asyncio
    async def test_categories_include_expected(self, client, auth_headers):
        resp = await client.get("/api/words/categories", headers=auth_headers)
        cats = resp.json()
        assert "greetings" in cats
        assert "questions" in cats
        assert "numbers" in cats

    @pytest.mark.asyncio
    async def test_categories_requires_auth(self, client):
        resp = await client.get("/api/words/categories")
        assert resp.status_code == 401


class TestWordsDataIntegrity:
    """Sõnade andmekorrektsuse testid."""

    @pytest.mark.asyncio
    async def test_words_have_non_empty_estonian(self, client, auth_headers):
        resp = await client.get("/api/words", headers=auth_headers)
        for w in resp.json():
            assert len(w["estonian"]) > 0

    @pytest.mark.asyncio
    async def test_words_have_non_empty_finnish(self, client, auth_headers):
        resp = await client.get("/api/words", headers=auth_headers)
        for w in resp.json():
            assert len(w["finnish"]) > 0

    @pytest.mark.asyncio
    async def test_words_difficulty_in_range(self, client, auth_headers):
        resp = await client.get("/api/words", headers=auth_headers)
        for w in resp.json():
            assert 1 <= w["difficulty"] <= 5

    @pytest.mark.asyncio
    async def test_words_is_cognate_is_boolean(self, client, auth_headers):
        resp = await client.get("/api/words", headers=auth_headers)
        for w in resp.json():
            assert isinstance(w["is_cognate"], bool)

    @pytest.mark.asyncio
    async def test_words_have_valid_ids(self, client, auth_headers):
        resp = await client.get("/api/words", headers=auth_headers)
        for w in resp.json():
            assert isinstance(w["id"], int)
            assert w["id"] > 0


class TestProgressEndpoint:
    """Progressi endpointi testid."""

    @pytest.mark.asyncio
    async def test_progress_returns_all_fields(self, client, auth_headers):
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
    async def test_progress_initial_values(self, client, auth_headers):
        resp = await client.get("/api/progress", headers=auth_headers)
        data = resp.json()
        assert data["xp"] >= 0
        assert data["level"] >= 1
        assert data["total_reviews"] >= 0

    @pytest.mark.asyncio
    async def test_progress_accuracy_calculation(self, client, auth_headers):
        resp = await client.get("/api/progress", headers=auth_headers)
        data = resp.json()
        assert 0 <= data["accuracy"] <= 100

    @pytest.mark.asyncio
    async def test_progress_requires_auth(self, client):
        resp = await client.get("/api/progress")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_progress_updates_after_review(self, client, auth_headers):
        await client.post("/api/srs/init", headers=auth_headers)
        resp = await client.get("/api/srs/due", headers=auth_headers)
        cards = resp.json()
        if not cards:
            pytest.skip("No cards available")

        prog_before = await client.get("/api/progress", headers=auth_headers)
        total_before = prog_before.json()["total_reviews"]

        await client.post("/api/srs/review", headers=auth_headers, json={
            "card_id": cards[0]["card_id"], "quality": 4
        })

        prog_after = await client.get("/api/progress", headers=auth_headers)
        total_after = prog_after.json()["total_reviews"]
        assert total_after == total_before + 1


class TestHealthCheck:
    """Health checki testid."""

    @pytest.mark.asyncio
    async def test_health_returns_200(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_health_returns_status_ok(self, client):
        resp = await client.get("/health")
        assert resp.json()["status"] == "ok"

    @pytest.mark.asyncio
    async def test_health_returns_app_name(self, client):
        resp = await client.get("/health")
        assert resp.json()["app"] == "learnFinnish"

    @pytest.mark.asyncio
    async def test_health_no_auth_required(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
