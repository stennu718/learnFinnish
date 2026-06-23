"""Unit tests for SM-2 SRS algorithm."""
import pytest
from app.services.srs import calculate_sm2


class TestSM2Algorithm:
    """Test the SM-2 spaced repetition algorithm."""

    def test_first_review_correct(self):
        """First correct review: interval=1, reps=1."""
        ef, interval, reps = calculate_sm2(quality=4, ease_factor=2.5, interval=0, repetitions=0)
        assert reps == 1
        assert interval == 1
        assert ef == 2.5  # EF unchanged at quality=4

    def test_first_review_perfect(self):
        """Perfect review boosts EF."""
        ef, interval, reps = calculate_sm2(quality=5, ease_factor=2.5, interval=0, repetitions=0)
        assert reps == 1
        assert interval == 1
        assert ef > 2.5

    def test_second_review_correct(self):
        """Second correct review: interval=6."""
        ef, interval, reps = calculate_sm2(quality=4, ease_factor=2.5, interval=1, repetitions=1)
        assert reps == 2
        assert interval == 6

    def test_third_review_correct(self):
        """Third correct review: interval = prev_interval * EF."""
        ef, interval, reps = calculate_sm2(quality=5, ease_factor=2.5, interval=6, repetitions=2)
        assert reps == 3
        assert interval == round(6 * 2.5)

    def test_failed_review_resets(self):
        """Failed review resets interval and reps."""
        ef, interval, reps = calculate_sm2(quality=1, ease_factor=2.5, interval=10, repetitions=5)
        assert reps == 0
        assert interval == 1

    def test_ef_minimum(self):
        """EF should never go below 1.3."""
        ef, _, _ = calculate_sm2(quality=0, ease_factor=1.3, interval=10, repetitions=5)
        assert ef >= 1.3

    def test_ef_decreases_on_wrong(self):
        """EF decreases on wrong answer."""
        ef, _, _ = calculate_sm2(quality=2, ease_factor=2.5, interval=10, repetitions=5)
        assert ef < 2.5

    def test_quality_3_borderline(self):
        """Quality 3 is the borderline for success."""
        ef, interval, reps = calculate_sm2(quality=3, ease_factor=2.5, interval=0, repetitions=0)
        assert reps == 1
        assert interval == 1

    def test_quality_0_complete_blackout(self):
        """Quality 0 is complete blackout."""
        ef, interval, reps = calculate_sm2(quality=0, ease_factor=2.0, interval=30, repetitions=10)
        assert reps == 0
        assert interval == 1
        assert ef < 2.0

    def test_long_streak_increases_interval(self):
        """Long streak should result in large intervals."""
        ef, interval, reps = 2.5, 0, 0
        for _ in range(10):
            ef, interval, reps = calculate_sm2(quality=4, ease_factor=ef, interval=interval, repetitions=reps)
        assert interval > 100
        assert reps == 10


class TestAuthUtils:
    """Test authentication utilities."""

    def test_hash_password(self):
        from app.core.auth import hash_password, verify_password
        hashed = hash_password("testpass123")
        assert hashed != "testpass123"
        assert hashed.startswith("$2b$")  # bcrypt prefix

    def test_verify_password_correct(self):
        from app.core.auth import hash_password, verify_password
        hashed = hash_password("testpass123")
        assert verify_password("testpass123", hashed) is True

    def test_verify_password_incorrect(self):
        from app.core.auth import hash_password, verify_password
        hashed = hash_password("testpass123")
        assert verify_password("wrongpass", hashed) is False

    def test_create_access_token(self):
        from app.core.auth import create_access_token
        from jose import jwt
        from app.core.config import settings

        token = create_access_token({"sub": 42})
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "42"  # sub is stored as string

    def test_token_contains_expiry(self):
        from app.core.auth import create_access_token
        from jose import jwt
        from app.core.config import settings

        token = create_access_token({"sub": 1})
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "exp" in payload


class TestWordPairModel:
    """Test WordPair model."""

    def test_create_word_pair(self):
        from app.models import WordPair
        pair = WordPair(
            estonian="tere",
            finnish="hei",
            estonian_example="Tere!",
            finnish_example="Hei!",
            category="greetings",
            is_cognate=False,
            difficulty=1
        )
        assert pair.estonian == "tere"
        assert pair.finnish == "hei"
        assert pair.category == "greetings"
        assert pair.is_cognate is False
        assert pair.difficulty == 1

    def test_cognate_detection(self):
        from app.models import WordPair
        pair = WordPair(
            estonian="vesi",
            finnish="vesi",
            is_cognate=True
        )
        assert pair.is_cognate is True


class TestSeedData:
    """Test seed data integrity."""

    def test_seed_json_valid(self):
        import json
        from app.services.seed import SEED_JSON
        words = json.loads(SEED_JSON)
        assert len(words) > 0
        for w in words:
            assert "estonian" in w
            assert "finnish" in w
            assert "et" in w
            assert "fi" in w
            assert "cat" in w
            assert "d" in w

    def test_seed_food_valid(self):
        from app.services.seed_food import SEED_PART2
        assert len(SEED_PART2) > 0
        for w in SEED_PART2:
            assert "estonian" in w
            assert "finnish" in w
            assert "cat" in w

    def test_seed_transport_valid(self):
        from app.services.seed_transport import SEED_PART3
        assert len(SEED_PART3) > 0

    def test_seed_shopping_valid(self):
        from app.services.seed_shopping import SEED_PART4
        assert len(SEED_PART4) > 0

    def test_seed_health_valid(self):
        from app.services.seed_health import SEED_PART5
        assert len(SEED_PART5) > 0

    def test_seed_home_time_valid(self):
        from app.services.seed_home_time import SEED_PART6
        assert len(SEED_PART6) > 0

    def test_seed_people_valid(self):
        from app.services.seed_people import SEED_PART7
        assert len(SEED_PART7) > 0

    def test_seed_clothing_nature_valid(self):
        from app.services.seed_clothing_nature import SEED_PART8
        assert len(SEED_PART8) > 0

    def test_all_categories_present(self):
        """Ensure all expected categories are present in seed data."""
        from app.services.seed import SEED_JSON
        import json
        words = json.loads(SEED_JSON)
        categories = set(w["cat"] for w in words)
        expected = {"greetings", "questions", "numbers"}
        assert expected.issubset(categories)

    def test_difficulty_range(self):
        """All difficulty values should be 1-5."""
        from app.services.seed import SEED_JSON
        import json
        words = json.loads(SEED_JSON)
        for w in words:
            assert 1 <= w["d"] <= 5, f"Difficulty out of range for {w['estonian']}: {w['d']}"
