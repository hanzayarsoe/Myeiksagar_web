"""CRF word-segmentation API used by the translator UI."""

from flask import jsonify, request

from config import MAX_SEGMENT_CHARS
from services.segmentation import segment_word


def register(app):
    @app.route("/translate", methods=["POST"])
    def wordTranslation():
        data = request.get_json(silent=True) or {}
        text = data.get("text")
        if not isinstance(text, str) or not text.strip():
            return jsonify({"error": "text is required"}), 400
        text = text.strip()
        if len(text) > MAX_SEGMENT_CHARS:
            return jsonify(
                {
                    "error": f"text must be at most {MAX_SEGMENT_CHARS} characters",
                }
            ), 400
        return jsonify({"translated_text": segment_word(text)})
