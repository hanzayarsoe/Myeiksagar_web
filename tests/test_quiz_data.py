"""Unit tests for quiz question bank helpers."""

from __future__ import annotations

import pytest

from quiz_data import (
    QUESTIONS,
    QUESTIONS_PER_ROUND,
    assert_quiz_integrity,
    pick_questions,
)
from routes.quiz import _normalize_answer


def test_assert_quiz_integrity_passes_for_bank():
    assert_quiz_integrity()  # raises on failure


def test_pick_questions_returns_requested_count():
    picked = pick_questions("easy", QUESTIONS_PER_ROUND)
    assert len(picked) == QUESTIONS_PER_ROUND
    assert all("question" in q and "answer" in q and "options" in q for q in picked)


def test_pick_questions_samples_without_duplicates_when_pool_large_enough():
    pool_size = len(QUESTIONS["easy"])
    assert pool_size >= QUESTIONS_PER_ROUND
    picked = pick_questions("easy", QUESTIONS_PER_ROUND)
    texts = [q["question"] for q in picked]
    assert len(texts) == len(set(texts))


def test_pick_questions_unknown_level_raises():
    with pytest.raises(ValueError, match="No questions configured"):
        pick_questions("legendary", 5)


def test_normalize_answer_strips_whitespace():
    assert _normalize_answer("  ပုလဲ  ") == "ပုလဲ"
    assert _normalize_answer(None) == ""
    assert _normalize_answer("") == ""
