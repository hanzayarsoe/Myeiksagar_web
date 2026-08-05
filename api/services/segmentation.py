"""CRF-based Myanmar word segmentation."""

from __future__ import annotations

import os

import pycrfsuite

from config import MODEL_PATH

_tagger = None


def get_tagger():
    """Lazy-load the CRF model so cold starts fail clearly and only when needed."""
    global _tagger
    if _tagger is None:
        if not os.path.isfile(MODEL_PATH):
            raise FileNotFoundError(f"CRF model not found at {MODEL_PATH}")
        tagger = pycrfsuite.Tagger()
        tagger.open(MODEL_PATH)
        _tagger = tagger
    return _tagger


def create_char_features(sentence, i):
    features = [
        "bias",
        "char=" + sentence[i][0],
    ]

    if i >= 1:
        features.extend(
            [
                "char-1=" + sentence[i - 1][0],
                "char-1:0=" + sentence[i - 1][0] + sentence[i][0],
            ]
        )
    else:
        features.append("BOS")

    if i >= 2:
        features.extend(
            [
                "char-2=" + sentence[i - 2][0],
                "char-2:0="
                + sentence[i - 2][0]
                + sentence[i - 1][0]
                + sentence[i][0],
                "char-2:-1=" + sentence[i - 2][0] + sentence[i - 1][0],
            ]
        )

    if i >= 3:
        features.extend(
            [
                "char-3:0="
                + sentence[i - 3][0]
                + sentence[i - 2][0]
                + sentence[i - 1][0]
                + sentence[i][0],
                "char-3:-1="
                + sentence[i - 3][0]
                + sentence[i - 2][0]
                + sentence[i - 1][0],
            ]
        )

    if i + 1 < len(sentence):
        features.extend(
            [
                "char+1=" + sentence[i + 1][0],
                "char:+1=" + sentence[i][0] + sentence[i + 1][0],
            ]
        )
    else:
        features.append("EOS")

    if i + 2 < len(sentence):
        features.extend(
            [
                "char+2=" + sentence[i + 2][0],
                "char:+2="
                + sentence[i][0]
                + sentence[i + 1][0]
                + sentence[i + 2][0],
                "char+1:+2=" + sentence[i + 1][0] + sentence[i + 2][0],
            ]
        )

    if i + 3 < len(sentence):
        features.extend(
            [
                "char:+3="
                + sentence[i][0]
                + sentence[i + 1][0]
                + sentence[i + 2][0]
                + sentence[i + 3][0],
                "char+1:+3="
                + sentence[i + 1][0]
                + sentence[i + 2][0]
                + sentence[i + 3][0],
            ]
        )
    return features


def create_word_features(prepared_sentence):
    return [
        create_char_features(prepared_sentence, i)
        for i in range(len(prepared_sentence))
    ]


def segment_word(sentence: str) -> str:
    """Insert spaces between CRF-predicted word boundaries."""
    sent = sentence.replace(" ", "")
    prediction = get_tagger().tag(create_word_features(sent))
    complete = ""
    for i, label in enumerate(prediction):
        if label == "1":
            complete += "   " + sent[i]
        else:
            complete += sent[i]
    return complete
