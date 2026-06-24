"""Grammar engine — Estonian-Finnish case transformation exercises.

Uses rule-based transformation with proper Finnish vowel harmony and stem detection.
"""
from dataclasses import dataclass


@dataclass
class CaseRule:
    name: str
    estonian_ending: str
    finnish_ending_back: str  # back vowels (a, o, u)
    finnish_ending_front: str  # front vowels (ä, ö, y)
    description: str
    examples: list[dict]


# Estonian -> Finnish case transformation rules
# Finnish vowel harmony: if word has back vowels (a,o,u) use back endings; if only front (ä,ö,y) use front
CASE_RULES = [
    CaseRule("inessive", "s", "ssa", "ssä",
             "Inessive: -s → -ssa/-ssä",
             [{"est": "talo", "fi": "talossa"}, {"est": "metsä", "fi": "metsässä"}]),

    CaseRule("elative", "st", "sta", "stä",
             "Elative: -st → -sta/-stä",
             [{"est": "talost", "fi": "talosta"}, {"est": "metsäst", "fi": "metsästä"}]),

    CaseRule("allative", "le", "lle", "lle",
             "Allative: -le → -lle (always)",
             [{"est": "pöydäle", "fi": "pöydälle"}, {"est": "lauale", "fi": "pöydälle"}]),

    CaseRule("adessive", "l", "lla", "llä",
             "Adessive: -l → -lla/-llä",
             [{"est": "laual", "fi": "pöydällä"}, {"est": "laual", "fi": "pöydällä"}]),

    CaseRule("ablative", "lt", "lta", "ltä",
             "Ablative: -lt → -lta/-ltä",
             [{"est": "laua lt", "fi": "pöydältä"}]),

    CaseRule("genitive", "", "n", "n",
             "Genitive: stem → stem + -n",
             [{"est": "maja", "fi": "talon"}, {"est": "metsä", "fi": "metsän"}]),

    CaseRule("partitive", "d/t", "ta", "tä",
             "Partitive: -d/-t → -ta/-tä",
             [{"est": "maad", "fi": "maata"}, {"est": "metsää", "fi": "metsää"}]),

    CaseRule("illative", "sse", "an", "än",
             "Illative: -sse → -an/-än/-een",
             [{"est": "taloon", "fi": "taloon"}, {"est": "metsään", "fi": "metsään"}]),

    CaseRule("translative", "ks", "ksi", "ksi",
             "Translative: -ks → -ksi",
             [{"est": "opettajaksi", "fi": "opettajaksi"}]),

    CaseRule("essive", "na", "na", "nä",
             "Essive: -na → -na/-nä",
             [{"est": "opettajana", "fi": "opettajana"}]),

    CaseRule("instructive", "tega", "lla", "llä",
             "Instructive: -tega → -lla/-llä",
             [{"est": "autoga", "fi": "autolla"}]),

    CaseRule("comitative", "ga", "ga", "gä",
             "Comitative: -ga → -ga/-gä",
             [{"est": "sõbraga", "fi": "ystävän kanssa"}]),
]


def has_back_vowels(word: str) -> bool:
    """Check if word has back vowels (a, o, u) — determines Finnish vowel harmony."""
    return bool(set(word.lower()) & set("aou"))


def get_finnish_ending(word: str, rule: CaseRule) -> str:
    """Get the correct Finnish ending based on vowel harmony."""
    # Check if word has only front vowels
    if not has_back_vowels(word):
        return rule.finnish_ending_front
    return rule.finnish_ending_back


def apply_rule(estonian_word: str, rule: CaseRule) -> str:
    """Apply a case transformation rule to an Estonian word.

    This is a simplified heuristic. For production use, consider:
    - omorfi (Finnish morphological analyzer)
    - libvoikki (Võro/Finnish morphology)
    - Custom ML model
    """
    # Remove Estonian ending
    if rule.estonian_ending and estonian_word.endswith(rule.estonian_ending):
        stem = estonian_word[:-len(rule.estonian_ending)]
    else:
        stem = estonian_word

    # Get correct Finnish ending based on vowel harmony
    ending = get_finnish_ending(stem, rule)

    # Special cases
    if rule.name == "illative":
        # Finnish illative often adds -een for back vowel words
        if has_back_vowels(stem) and not stem.endswith("e"):
            return stem + "een"
        return stem + ending

    if rule.name == "genitive":
        return stem + ending

    return stem + ending


def get_all_rules() -> list[CaseRule]:
    return CASE_RULES


def get_rule_by_name(name: str) -> CaseRule | None:
    for rule in CASE_RULES:
        if rule.name == name:
            return rule
    return None


def generate_exercise(rule: CaseRule) -> dict:
    """Generate a grammar exercise."""
    import random
    example = random.choice(rule.examples)
    return {
        "rule_name": rule.name,
        "description": rule.description,
        "estonian": example["est"],
        "finnish": example["fi"],
        "estonian_sentence": example.get("et", ""),
        "finnish_sentence": example.get("fi_sentence", example["fi"]),
    }


def generate_all_exercises() -> list[dict]:
    exercises = []
    for rule in CASE_RULES:
        for example in rule.examples:
            exercises.append({
                "rule_name": rule.name,
                "description": rule.description,
                "estonian": example["est"],
                "finnish": example["fi"],
                "estonian_sentence": example.get("et", ""),
                "finnish_sentence": example.get("fi_sentence", example["fi"]),
            })
    return exercises
