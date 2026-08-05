"""Vercel / local entrypoint — keeps a top-level Flask `app` for the runtime."""

from __future__ import annotations

import os
import sys

API_DIR = os.path.dirname(os.path.abspath(__file__))
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)

from factory import create_app

app = create_app()


def _debug_enabled() -> bool:
    """Opt-in local debug only; never enable on Vercel / production."""
    if os.environ.get("VERCEL") or os.environ.get("FLASK_ENV") == "production":
        return False
    return os.environ.get("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}


if __name__ == "__main__":
    app.run(debug=_debug_enabled())
