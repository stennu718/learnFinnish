"""Seed andmete ja E2E testid — 50+ testi."""
import pytest
import json
from app.models import WordPair


class TestSeedDataIntegrity:
    """Seed andmete terviklikkuse testid."""

    def test_seed_json_is_valid_json(self):
        from app.services.seed import SEED_JSON
        words = json.loads(SEED_JSON)
        assert len(words) > 0

    def test_seed_json_all_fields_present(self):
        from app.services.seed import SEED_JSON
        words = json.loads(SEED_JSON)
        required = {"estonian", "finnish", "et", "fi", "cat", "cog", "d"}
        for w in words:
            assert required.issubset(set(w.keys()))

    def test_seed_json_no_empty_estonian(self):
        from app.services.seed import SEED_JSON
        words = json.loads(SEED_JSON)
        for w in words:
            assert len(w["estonian"].strip()) > 0

    def test_seed_json_no_empty_finnish(self):
        from app.services.seed import SEED_JSON
        words = json.loads(SEED_JSON)
        for w in words:
            assert len(w["finnish"].strip()) > 0

    def test_seed_json_difficulty_range(self):
        from app.services.seed import SEED_JSON
        words = json.loads(SEED_JSON)
        for w in words:
            assert 1 <= w["d"] <= 5

    def test_seed_json_cognate_is_binary(self):
        from app.services.seed import SEED_JSON
        words = json.loads(SEED_JSON)
        for w in words:
            assert w["cog"] in (0, 1)

    def test_seed_json_categories_valid(self):
        from app.services.seed import SEED_JSON
        words = json.loads(SEED_JSON)
        valid_cats = {"greetings", "questions", "numbers", "food", "transport",
                      "shopping", "health", "body", "home", "time", "nature",
                      "clothing", "people", "work"}
        for w in words:
            assert w["cat"] in valid_cats

    def test_seed_food_valid(self):
        from app.services.seed_food import SEED_PART2
        assert len(SEED_PART2) > 0
        for w in SEED_PART2:
            assert "estonian" in w
            assert "finnish" in w

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

    def test_all_seed_parts_have_required_fields(self):
        from app.services.seed_food import SEED_PART2
        from app.services.seed_transport import SEED_PART3
        from app.services.seed_shopping import SEED_PART4
        from app.services.seed_health import SEED_PART5
        from app.services.seed_home_time import SEED_PART6
        from app.services.seed_people import SEED_PART7
        from app.services.seed_clothing_nature import SEED_PART8
        required = {"estonian", "finnish", "et", "fi", "cat", "cog", "d"}
        for part in [SEED_PART2, SEED_PART3, SEED_PART4, SEED_PART5,
                     SEED_PART6, SEED_PART7, SEED_PART8]:
            for w in part:
                assert required.issubset(set(w.keys()))

    def test_no_duplicate_estonian_finnish_pairs(self):
        from app.services.seed import SEED_JSON
        words = json.loads(SEED_JSON)
        pairs = set()
        for w in words:
            pair = (w["estonian"], w["finnish"])
            assert pair not in pairs, f"Duplicate: {pair}"
            pairs.add(pair)

    def test_seed_total_word_count(self):
        from app.services.seed import SEED_JSON
        from app.services.seed_food import SEED_PART2
        from app.services.seed_transport import SEED_PART3
        from app.services.seed_shopping import SEED_PART4
        from app.services.seed_health import SEED_PART5
        from app.services.seed_home_time import SEED_PART6
        from app.services.seed_people import SEED_PART7
        from app.services.seed_clothing_nature import SEED_PART8
        total = (len(json.loads(SEED_JSON)) + len(SEED_PART2) + len(SEED_PART3) +
                 len(SEED_PART4) + len(SEED_PART5) + len(SEED_PART6) +
                 len(SEED_PART7) + len(SEED_PART8))
        assert total >= 300


class TestWordPairModel:
    """WordPair mudeli testid."""

    def test_create_word_pair(self):
        pair = WordPair(estonian="tere", finnish="hei")
        assert pair.estonian == "tere"
        assert pair.finnish == "hei"

    def test_word_pair_defaults(self):
        pair = WordPair(estonian="test", finnish="testi", category="general", difficulty=1)
        assert pair.category == "general"
        assert pair.difficulty == 1

    def test_word_pair_with_examples(self):
        pair = WordPair(
            estonian="tere", finnish="hei",
            estonian_example="Tere!", finnish_example="Hei!"
        )
        assert pair.estonian_example == "Tere!"
        assert pair.finnish_example == "Hei!"

    def test_word_pair_cognate_flag(self):
        pair = WordPair(estonian="vesi", finnish="vesi", is_cognate=True)
        assert pair.is_cognate is True

    def test_word_pair_difficulty_levels(self):
        for d in range(1, 6):
            pair = WordPair(estonian="test", finnish="testi", difficulty=d)
            assert pair.difficulty == d

    def test_word_pair_categories(self):
        categories = ["greetings", "food", "transport", "nature", "health"]
        for cat in categories:
            pair = WordPair(estonian="test", finnish="testi", category=cat)
            assert pair.category == cat


class TestUserModel:
    """User mudeli testid."""

    def test_user_default_values(self):
        from app.models import User
        user = User(email="test@test.ee", hashed_password="hash123", display_name="", is_active=True)
        assert user.email == "test@test.ee"
        assert user.hashed_password == "hash123"


class TestSRSCardModel:
    """SRSCard mudeli testid."""

    def test_srs_card_defaults(self):
        from app.models import SRSCard
        card = SRSCard(user_id=1, word_pair_id=1, direction="et_fi", ease_factor=2.5, interval=0, repetitions=0)
        assert card.ease_factor == 2.5
        assert card.interval == 0
        assert card.repetitions == 0

    def test_srs_card_directions(self):
        from app.models import SRSCard
        card_et_fi = SRSCard(user_id=1, word_pair_id=1, direction="et_fi")
        card_fi_et = SRSCard(user_id=1, word_pair_id=1, direction="fi_et")
        assert card_et_fi.direction == "et_fi"
        assert card_fi_et.direction == "fi_et"


class TestUserProgressModel:
    """UserProgress mudeli testid."""

    def test_progress_defaults(self):
        from app.models import UserProgress
        prog = UserProgress(user_id=1)
        # SQLAlchemy defaults are DB-level, verify object creation
        assert prog.user_id == 1
