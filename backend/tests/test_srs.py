"""Tests for SM-2 SRS algorithm."""
import pytest
from app.services.srs import calculate_sm2


def test_sm2_first_correct():
    ef, interval, reps = calculate_sm2(quality=4, ease_factor=2.5, interval=0, repetitions=0)
    assert reps == 1
    assert interval == 1
    # EF = 2.5 + (0.1 - (5-4)*(0.08+(5-4)*0.02)) = 2.5 + (0.1 - 0.10) = 2.5
    assert ef == 2.5


def test_sm2_first_perfect():
    """Quality 5 should boost EF."""
    ef, interval, reps = calculate_sm2(quality=5, ease_factor=2.5, interval=0, repetitions=0)
    assert reps == 1
    assert interval == 1
    assert ef > 2.5


def test_sm2_second_correct():
    ef, interval, reps = calculate_sm2(quality=4, ease_factor=2.5, interval=1, repetitions=1)
    assert reps == 2
    assert interval == 6


def test_sm2_third_correct():
    ef, interval, reps = calculate_sm2(quality=5, ease_factor=2.5, interval=6, repetitions=2)
    assert reps == 3
    assert interval == round(6 * 2.5)


def test_sm2_failed_resets():
    ef, interval, reps = calculate_sm2(quality=1, ease_factor=2.5, interval=10, repetitions=5)
    assert reps == 0
    assert interval == 1


def test_sm2_ef_minimum():
    ef, _, _ = calculate_sm2(quality=0, ease_factor=1.3, interval=10, repetitions=5)
    assert ef >= 1.3


def test_sm2_perfect_boosts_ef():
    ef, _, _ = calculate_sm2(quality=5, ease_factor=2.5, interval=1, repetitions=0)
    assert ef > 2.5
