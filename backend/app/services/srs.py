"""SM-2 Spaced Repetition Algorithm."""


def calculate_sm2(
    quality: int,
    ease_factor: float,
    interval: int,
    repetitions: int,
) -> tuple[float, int, int]:
    """
    SM-2 algorithm implementation.
    quality: 0-5 (0=complete blackout, 5=perfect)
    Returns: (new_ease_factor, new_interval, new_repetitions)
    """
    if quality < 3:
        # Failed — reset
        new_repetitions = 0
        new_interval = 1
    else:
        new_repetitions = repetitions + 1
        if new_repetitions == 1:
            new_interval = 1
        elif new_repetitions == 2:
            new_interval = 6
        else:
            new_interval = round(interval * ease_factor)

    # Update ease factor
    new_ef = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if new_ef < 1.3:
        new_ef = 1.3

    return new_ef, new_interval, new_repetitions
