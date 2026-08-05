"""Paths and runtime configuration for the Myeiksagar Flask app."""

from __future__ import annotations

import os

API_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(API_DIR)
MODEL_PATH = os.path.join(API_DIR, "mm-word-segmentation-300.crfsuite")
TEMPLATE_FOLDER = os.path.join(API_DIR, "templates")
STATIC_FOLDER = os.path.join(ROOT_DIR, "public", "static")

MAX_SEGMENT_CHARS = 2000
DEV_SECRET_FALLBACK = "dev-only-insecure-secret-key"


def load_dotenv() -> None:
    """Load KEY=VALUE pairs from .env / .env.local files (not a .env/ directory)."""
    for name in (".env", ".env.local"):
        env_path = os.path.join(ROOT_DIR, name)
        if not os.path.isfile(env_path):
            continue
        with open(env_path, encoding="utf-8") as env_file:
            for raw_line in env_file:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip("'").strip('"')
                if key:
                    os.environ.setdefault(key, value)


def secret_key() -> str:
    value = os.environ.get("SECRET_KEY")
    if value:
        return value
    if os.environ.get("VERCEL"):
        raise RuntimeError(
            "SECRET_KEY is required on Vercel. "
            "Set it in Project Settings → Environment Variables."
        )
    return DEV_SECRET_FALLBACK


def session_config() -> dict:
    return {
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": bool(os.environ.get("VERCEL")),
    }
