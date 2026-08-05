"""Flask test-client happy paths (no Firebase required)."""

from __future__ import annotations

from unittest.mock import patch


def test_home_page_ok(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"html" in response.data.lower() or response.mimetype == "text/html"


def test_quiz_start_page_ok(client):
    response = client.get("/quiz_start_page")
    assert response.status_code == 200


def test_translate_happy_path_mocks_segmenter(client):
    with patch(
        "routes.translate.segment_word",
        return_value="မြန်   မာ",
    ) as mock_segment:
        response = client.post(
            "/translate",
            json={"text": "မြန်မာ"},
        )

    assert response.status_code == 200
    assert response.get_json() == {"translated_text": "မြန်   မာ"}
    mock_segment.assert_called_once_with("မြန်မာ")


def test_translate_rejects_empty_text(client):
    response = client.post("/translate", json={"text": "   "})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_translate_rejects_oversized_text(client):
    from config import MAX_SEGMENT_CHARS

    response = client.post(
        "/translate",
        json={"text": "က" * (MAX_SEGMENT_CHARS + 1)},
    )
    assert response.status_code == 400
    body = response.get_json()
    assert "error" in body
    assert str(MAX_SEGMENT_CHARS) in body["error"]
