"""Grammar engine — Estonian-Finnish case transformation exercises."""
import re
from dataclasses import dataclass


@dataclass
class CaseRule:
    """Estonian to Finnish case transformation rule."""
    name: str
    estonian_ending: str
    finnish_ending: str
    description: str
    examples: list[dict]


# Estonian -> Finnish case transformation rules
CASE_RULES = [
    CaseRule(
        name="inessive",
        estonian_ending="s",
        finnish_ending="ssa",
        description="Inessive (sees): Estonian -s → Finnish -ssa/-ssä",
        examples=[
            {"est": "majas", "fi": "talossa", "et": "Olen majas.", "fi": "Olen talossa."},
            {"est": "koolis", "fi": "koulussa", "et": "Õpilane on koolis.", "fi": "Opiskelija on koulussa."},
        ]
    ),
    CaseRule(
        name="elative",
        estonian_ending="st",
        finnish_ending="sta",
        description="Elative (seest): Estonian -st → Finnish -sta/-stä",
        examples=[
            {"est": "majast", "fi": "talosta", "et": "Tulen majast.", "fi": "Tulen talosta."},
        ]
    ),
    CaseRule(
        name="allative",
        estonian_ending="le",
        finnish_ending="lle",
        description="Allative (peale): Estonian -le → Finnish -lle",
        examples=[
            {"est": "laua", "fi": "pöydälle", "et": "Pane lauale.", "fi": "Laita pöydälle."},
        ]
    ),
    CaseRule(
        name="adessive",
        estonian_ending="l",
        finnish_ending="lla",
        description="Adessive (peal): Estonian -l → Finnish -lla/-llä",
        examples=[
            {"est": "laual", "fi": "pöydällä", "et": "Raamat on laual.", "fi": "Kirja on pöydällä."},
        ]
    ),
    CaseRule(
        name="ablative",
        estonian_ending="lt",
        finnish_ending="lta",
        description="Ablative (pealt): Estonian -lt → Finnish -lta/-ltä",
        examples=[
            {"est": "laua", "fi": "pöydältä", "et": "Võta laua pealt.", "fi": "Ota pöydältä."},
        ]
    ),
    CaseRule(
        name="genitive",
        estonian_ending="",
        finnish_ending="n",
        description="Genitive (omastav): Estonian -∅ → Finnish -n",
        examples=[
            {"est": "maja", "fi": "talon", "et": "Maja uks.", "fi": "Talon ovi."},
        ]
    ),
    CaseRule(
        name="partitive",
        estonian_ending="d/t",
        finnish_ending="a/ta",
        description="Partitive (osastav): Estonian -d/-t → Finnish -a/-ta",
        examples=[
            {"est": "maad", "fi": "maata", "et": "Ma näen maad.", "fi": "Näen maata."},
        ]
    ),
    CaseRule(
        name="illative",
        estonian_ending="sse",
        finnish_ending="an/ään",
        description="Illative (sisse): Estonian -sse → Finnish -an/-ään",
        examples=[
            {"est": "majja", "fi": "taloon", "et": "Lähen majja.", "fi": "Menen taloon."},
        ]
    ),
    CaseRule(
        name="translative",
        estonian_ending="ks",
        finnish_ending="ksi",
        description="Translative (saav): Estonian -ks → Finnish -ksi",
        examples=[
            {"est": "õpetajaks", "fi": "opettajaksi", "et": "Hakka õpetajaks!", "fi": "Ryhdy opettajaksi!"},
        ]
    ),
    CaseRule(
        name="essive",
        estonian_ending="na",
        finnish_ending="na",
        description="Essive (kui): Estonian -na → Finnish -na",
        examples=[
            {"est": "õpetajana", "fi": "opettajana", "et": "Kui õpetajana ma töötlen.", "fi": "Opettajana työskentelen."},
        ]
    ),
    CaseRule(
        name="instructive",
        estonian_ending="tega",
        finnish_ending="lla",
        description="Instructive (kaasa): Estonian -tega → Finnish -lla",
        examples=[
            {"est": "autoga", "fi": "autolla", "et": "Lähen autoga.", "fi": "Menen autolla."},
        ]
    ),
    CaseRule(
        name="comitative",
        estonian_ending="ga",
        finnish_ending="ga",
        description="Comitative (koos): Estonian -ga → Finnish -ga (rare)",
        examples=[
            {"est": "sõbraga", "fi": "ystävän kanssa", "et": "Lähen sõbraga.", "fi": "Menen ystävän kanssa."},
        ]
    ),
]


def get_all_rules() -> list[CaseRule]:
    """Return all case transformation rules."""
    return CASE_RULES


def get_rule_by_name(name: str) -> CaseRule | None:
    """Get a specific case rule by name."""
    for rule in CASE_RULES:
        if rule.name == name:
            return rule
    return None


def apply_rule(word: str, rule: CaseRule) -> str:
    """Apply a case transformation rule to an Estonian word."""
    # Simple heuristic: replace ending
    if word.endswith(rule.estonian_ending):
        return word[:-len(rule.estonian_ending)] + rule.finnish_ending
    return word + rule.finnish_ending


def generate_exercise(rule: CaseRule) -> dict:
    """Generate a grammar exercise for a specific rule."""
    import random
    example = random.choice(rule.examples)
    return {
        "rule_name": rule.name,
        "description": rule.description,
        "estonian": example["est"],
        "finnish": example["fi"],
        "estonian_sentence": example["et"],
        "finnish_sentence": example["fi"],
    }


def generate_all_exercises() -> list[dict]:
    """Generate exercises for all rules."""
    exercises = []
    for rule in CASE_RULES:
        for example in rule.examples:
            exercises.append({
                "rule_name": rule.name,
                "description": rule.description,
                "estonian": example["est"],
                "finnish": example["fi"],
                "estonian_sentence": example["et"],
                "finnish_sentence": example["fi"],
            })
    return exercises
