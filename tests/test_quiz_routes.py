"""Quiz route flow via Flask test client (session-based, offline)."""

from __future__ import annotations

from contextlib import contextmanager
from unittest.mock import patch

FAKE_QUESTION = {
    "question": "Fake Myeik question?",
    "options": ["correct", "wrong-a", "wrong-b"],
    "answer": "correct",
}


@contextmanager
def short_quiz_round(questions=None):
    """One-question rounds so progression tests stay fast and deterministic."""
    qs = list(questions) if questions is not None else [FAKE_QUESTION]
    with patch("routes.quiz.QUESTIONS_PER_ROUND", len(qs)), patch(
        "routes.quiz.pick_questions", return_value=qs
    ):
        yield qs


def test_quiz_redirects_to_start_without_session(client):
    response = client.get("/quiz")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/quiz_start_page")


def test_quiz_start_initializes_session_and_shows_question(client):
    with short_quiz_round():
        response = client.get("/quiz_start", follow_redirects=True)

    assert response.status_code == 200
    assert b"Fake Myeik question?" in response.data
    with client.session_transaction() as sess:
        assert sess["level"] == "easy"
        assert sess["score"] == 0
        assert sess["question_number"] == 0
        assert sess["completed_levels"] == 0
        assert sess["total_questions"] == 1


def test_wrong_answer_redirects_to_result(client):
    with short_quiz_round():
        client.get("/quiz_start", follow_redirects=True)
        response = client.post(
            "/quiz",
            data={"answer": "wrong-a"},
            follow_redirects=True,
        )

    assert response.status_code == 200
    assert b"result" in response.data.lower() or b"score" in response.data.lower()
    with client.session_transaction() as sess:
        assert sess["score"] == 0
        assert sess["question_number"] == 1


def test_perfect_easy_round_redirects_to_next_level(client):
    with short_quiz_round():
        client.get("/quiz_start", follow_redirects=True)
        response = client.post(
            "/quiz",
            data={"answer": "correct"},
            follow_redirects=True,
        )

    assert response.status_code == 200
    assert b"medium" in response.data.lower() or b"next" in response.data.lower()
    with client.session_transaction() as sess:
        assert sess["score"] == 1
        assert sess["completed_levels"] == 1
        assert sess["level"] == "easy"


def test_answer_whitespace_normalized_as_correct(client):
    with short_quiz_round():
        client.get("/quiz_start", follow_redirects=True)
        client.post("/quiz", data={"answer": "  correct  "}, follow_redirects=True)

    with client.session_transaction() as sess:
        assert sess["score"] == 1
        assert sess["completed_levels"] == 1


def test_start_next_level_advances_easy_to_medium(client):
    with short_quiz_round():
        client.get("/quiz_start", follow_redirects=True)
        client.post("/quiz", data={"answer": "correct"}, follow_redirects=True)
        response = client.get("/start_next_level", follow_redirects=True)

    assert response.status_code == 200
    assert b"Fake Myeik question?" in response.data
    with client.session_transaction() as sess:
        assert sess["level"] == "medium"
        assert sess["score"] == 0
        assert sess["question_number"] == 0
        assert sess["completed_levels"] == 1


def test_next_level_requires_completed_levels(client):
    response = client.get("/next_level")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/quiz_start_page")


def test_start_next_level_requires_completed_levels(client):
    response = client.get("/start_next_level")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/quiz_start_page")


def test_perfect_hard_round_redirects_to_congratulations(client):
    with short_quiz_round():
        with client.session_transaction() as sess:
            sess["level"] = "hard"
            sess["score"] = 0
            sess["question_number"] = 0
            sess["completed_levels"] = 2
            sess["questions"] = [FAKE_QUESTION]
            sess["total_questions"] = 1

        response = client.post(
            "/quiz",
            data={"answer": "correct"},
            follow_redirects=True,
        )

    assert response.status_code == 200
    assert (
        b"congratulat" in response.data.lower()
        or b"congrats" in response.data.lower()
        or b"complete" in response.data.lower()
    )
    with client.session_transaction() as sess:
        # congratulations clears completed_levels after render gate
        assert sess.get("completed_levels", 0) == 0


def test_congratulations_requires_three_completed_levels(client):
    with client.session_transaction() as sess:
        sess["completed_levels"] = 2

    response = client.get("/congratulations")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/quiz_start_page")


def test_result_requires_level_in_session(client):
    response = client.get("/result")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/quiz_start_page")


def test_result_renders_score_when_session_present(client):
    with client.session_transaction() as sess:
        sess["level"] = "easy"
        sess["score"] = 3
        sess["total_questions"] = 10

    response = client.get("/result")
    assert response.status_code == 200
    assert b"3" in response.data
