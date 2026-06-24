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
CASE_RULES = [
    CaseRule("inessive", "s", "ssa", "ssä",
             "Inessive: -s → -ssa/-ssä",
             [{"est": "talo", "fi": "talossa"}, {"est": "metsä", "fi": "metsässä"}]),

    CaseRule("elative", "st", "sta", "stä",
             "Elative: -st → -sta/-stä",
             [{"est": "talost", "fi": "talosta"}, {"est": "metsäst", "fi": "metsästä"}]),

    CaseRule("allative", "le", "lle", "lle",
             "Allative: -le → -lle",
             [{"est": "pöydäle", "fi": "pöydälle"}, {"est": "lauval", "fi": "pöydälle"}]),

    CaseRule("adessive", "l", "lla", "llä",
             "Adessive: -l → -lla/-llä",
             [{"est": "laual", "fi": "pöydällä"}, {"est": "pöydäl", "fi": "pöydällä"}]),

    CaseRule("ablative", "lt", "lta", "ltä",
             "Ablative: -lt → -lta/-ltä",
             [{"est": "laualt", "fi": "pöydältä"}, {"est": "pöydält", "fi": "pöydältä"}]),

    CaseRule("genitive", "", "n", "n",
             "Genitive: stem → stem + -n",
             [{"est": "maja", "fi": "majan"}, {"est": "talo", "fi": "talon"}]),

    CaseRule("partitive", "d/t", "ta", "tä",
             "Partitive: -d/-t → -ta/-tä",
             [{"est": "maad", "fi": "maata"}, {"est": "maata", "fi": "maata"}]),

    CaseRule("illative", "sse", "an", "än",
             "Illative: -sse → -an/-än/-seen",
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
    if not has_back_vowels(word):
        return rule.finnish_ending_front
    return rule.finnish_ending_back


def apply_rule(estonian_word: str, rule: CaseRule) -> str:
    """Apply a case transformation rule to an Estonian word."""
    # Remove Estonian ending
    if rule.estonian_ending and estonian_word.endswith(rule.estonian_ending):
        stem = estonian_word[:-len(rule.estonian_ending)]
    else:
        stem = estonian_word

    ending = get_finnish_ending(stem, rule)

    # Special cases
    if rule.name == "illative":
        # Finnish illative (sisseütlev):
        # - Words ending in -e: stem + "en" (näe → näen)
        # - Words ending in vowel: stem + stem[-1] + "n" (talo → taloon, koulu → kouluun, auto → autoon)
        # - Words ending in consonant: stem + "seen" (talo → taloon is wrong, actually talo ends in vowel)
        if stem.endswith("e"):
            return stem + "en"
        elif stem[-1] in "aeiouyäö":
            # Vowel ending: double the last vowel + n
            return stem + stem[-1] + "n"
        else:
            # Consonant ending
            return stem + "seen"

    if rule.name == "genitive":
        return stem + ending

    if rule.name == "partitive":
        # If word already ends in vowel, just add -ta/-tä
        if stem and stem[-1] in "aeiouyäö":
            return stem + ending
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
