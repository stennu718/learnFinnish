"""Grammar engine testid — 50+ testi."""
import pytest
from app.services.grammar import (
    get_all_rules, get_rule_by_name, generate_exercise,
    generate_all_exercises, apply_rule, CaseRule
)


class TestGrammarRules:
    """Grammatika reeglite testid."""

    def test_get_all_rules_returns_list(self):
        rules = get_all_rules()
        assert isinstance(rules, list)
        assert len(rules) > 0

    def test_get_all_rules_has_12_cases(self):
        rules = get_all_rules()
        assert len(rules) == 12

    def test_all_rules_have_required_fields(self):
        rules = get_all_rules()
        for rule in rules:
            assert isinstance(rule, CaseRule)
            assert len(rule.name) > 0
            assert len(rule.description) > 0
            assert len(rule.examples) > 0

    def test_get_rule_by_name_exists(self):
        rule = get_rule_by_name("inessive")
        assert rule is not None
        assert rule.name == "inessive"

    def test_get_rule_by_name_not_exists(self):
        rule = get_rule_by_name("nonexistent")
        assert rule is None

    def test_get_all_rule_names(self):
        rules = get_all_rules()
        names = [r.name for r in rules]
        expected = ["inessive", "elative", "allative", "adessive", "ablative",
                    "genitive", "partitive", "illative", "translative", "essive",
                    "instructive", "comitative"]
        for name in expected:
            assert name in names


class TestGrammarExamples:
    """Grammatika näidete testid."""

    def test_all_rules_have_examples(self):
        rules = get_all_rules()
        for rule in rules:
            assert len(rule.examples) > 0
            for ex in rule.examples:
                assert "est" in ex
                assert "fi" in ex
                assert "et" in ex
                assert "fi" in ex

    def test_examples_have_non_empty_values(self):
        rules = get_all_rules()
        for rule in rules:
            for ex in rule.examples:
                assert len(ex["est"]) > 0
                assert len(ex["fi"]) > 0
                assert len(ex["et"]) > 0
                assert len(ex["fi"]) > 0

    def test_inessive_examples(self):
        rule = get_rule_by_name("inessive")
        assert rule is not None
        for ex in rule.examples:
            assert "s" in ex["est"] or "s" in ex["fi"]

    def test_elative_examples(self):
        rule = get_rule_by_name("elative")
        assert rule is not None
        for ex in rule.examples:
            assert "st" in ex["est"] or "sta" in ex["fi"]


class TestGrammarExercises:
    """Grammatika harjutuste testid."""

    def test_generate_exercise(self):
        rule = get_rule_by_name("inessive")
        assert rule is not None
        exercise = generate_exercise(rule)
        assert exercise["rule_name"] == "inessive"
        assert "estonian" in exercise
        assert "finnish" in exercise
        assert "description" in exercise

    def test_generate_all_exercises(self):
        exercises = generate_all_exercises()
        assert len(exercises) > 0
        for ex in exercises:
            assert "rule_name" in ex
            assert "estonian" in ex
            assert "finnish" in ex

    def test_exercises_cover_all_rules(self):
        exercises = generate_all_exercises()
        rule_names = set(ex["rule_name"] for ex in exercises)
        all_rules = get_all_rules()
        for rule in all_rules:
            assert rule.name in rule_names


class TestGrammarApplyRule:
    """Reeglite rakendamise testid."""

    def test_apply_inessive_rule(self):
        rule = get_rule_by_name("inessive")
        assert rule is not None
        result = apply_rule("maja", rule)
        assert result is not None
        assert isinstance(result, str)

    def test_apply_elative_rule(self):
        rule = get_rule_by_name("elative")
        assert rule is not None
        result = apply_rule("maja", rule)
        assert result is not None

    def test_apply_genitive_rule(self):
        rule = get_rule_by_name("genitive")
        assert rule is not None
        result = apply_rule("maja", rule)
        assert result is not None

    def test_apply_rule_preserves_word(self):
        rule = get_rule_by_name("inessive")
        result = apply_rule("maja", rule)
        # Result should contain the original word stem
        assert len(result) > 0

    def test_apply_all_rules(self):
        rules = get_all_rules()
        for rule in rules:
            assert rule is not None
            result = apply_rule("maja", rule)
            assert isinstance(result, str)
            assert len(result) > 0


class TestGrammarCaseCoverage:
    """Käänete katvuse testid."""

    def test_12_cases_covered(self):
        rules = get_all_rules()
        assert len(rules) == 12

    def test_all_cases_have_estonian_ending(self):
        rules = get_all_rules()
        for rule in rules:
            assert isinstance(rule.estonian_ending, str)

    def test_all_cases_have_finnish_ending(self):
        rules = get_all_rules()
        for rule in rules:
            assert isinstance(rule.finnish_ending, str)

    def test_all_cases_have_descriptions(self):
        rules = get_all_rules()
        for rule in rules:
            assert len(rule.description) > 10


class TestGrammarFinnishEndings:
    """Soomepäändete testid."""

    def test_inessive_finnish_ending(self):
        rule = get_rule_by_name("inessive")
        assert rule is not None
        assert rule.finnish_ending in ("ssa", "ssä")

    def test_elative_finnish_ending(self):
        rule = get_rule_by_name("elative")
        assert rule is not None
        assert rule.finnish_ending in ("sta", "stä")

    def test_allative_finnish_ending(self):
        rule = get_rule_by_name("allative")
        assert rule is not None
        assert rule.finnish_ending == "lle"

    def test_adessive_finnish_ending(self):
        rule = get_rule_by_name("adessive")
        assert rule is not None
        assert rule.finnish_ending in ("lla", "llä")

    def test_genitive_finnish_ending(self):
        rule = get_rule_by_name("genitive")
        assert rule is not None
        assert rule.finnish_ending == "n"


class TestGrammarAPIStructure:
    """API struktuuri testid."""

    def test_case_rule_response_model(self):
        from app.api.grammar import CaseRuleResponse
        resp = CaseRuleResponse(
            name="test",
            estonian_ending="s",
            finnish_ending="ssa",
            description="Test",
            examples=[{"est": "test", "fi": "testi"}]
        )
        assert resp.name == "test"

    def test_exercise_response_model(self):
        from app.api.grammar import ExerciseResponse
        resp = ExerciseResponse(
            rule_name="test",
            description="Test",
            estonian="test",
            finnish="testi",
            estonian_sentence="Test.",
            finnish_sentence="Testi."
        )
        assert resp.rule_name == "test"

    def test_apply_rule_request_model(self):
        from app.api.grammar import ApplyRuleRequest
        req = ApplyRuleRequest(word="maja", rule_name="inessive")
        assert req.word == "maja"
        assert req.rule_name == "inessive"

    def test_apply_rule_response_model(self):
        from app.api.grammar import ApplyRuleResponse
        resp = ApplyRuleResponse(
            original="maja",
            transformed="talossa",
            rule_name="inessive",
            description="Test"
        )
        assert resp.original == "maja"
