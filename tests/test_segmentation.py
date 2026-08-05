"""Unit tests for CRF segmentation helpers (tagger mocked where needed)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from services import segmentation
from services.segmentation import (
    create_char_features,
    create_word_features,
    segment_word,
)


def test_create_char_features_marks_bos_and_eos():
    sentence = "က"
    features = create_char_features(sentence, 0)
    assert "bias" in features
    assert "char=က" in features
    assert "BOS" in features
    assert "EOS" in features


def test_create_char_features_includes_neighbors():
    sentence = "abc"
    features = create_char_features(sentence, 1)
    assert "char=b" in features
    assert "char-1=a" in features
    assert "char+1=c" in features
    assert "BOS" not in features
    assert "EOS" not in features


def test_create_word_features_one_list_per_char():
    prepared = "မြန်"
    features = create_word_features(prepared)
    assert len(features) == len(prepared)
    assert all(isinstance(row, list) for row in features)


def test_segment_word_inserts_spaces_on_boundary_labels():
    mock_tagger = MagicMock()
    mock_tagger.tag.return_value = ["0", "1", "0"]

    with patch.object(segmentation, "get_tagger", return_value=mock_tagger):
        result = segment_word("a b c")  # spaces stripped before tagging

    assert result == "a   bc"
    mock_tagger.tag.assert_called_once()
    tagged_features = mock_tagger.tag.call_args[0][0]
    assert len(tagged_features) == 3


def test_get_tagger_raises_when_model_missing(tmp_path, monkeypatch):
    segmentation._tagger = None
    missing = tmp_path / "missing.crfsuite"
    monkeypatch.setattr(segmentation, "MODEL_PATH", str(missing))

    with pytest.raises(FileNotFoundError, match="CRF model not found"):
        segmentation.get_tagger()

    segmentation._tagger = None
