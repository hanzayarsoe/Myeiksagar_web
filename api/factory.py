"""Flask application factory."""

from flask import Flask

from config import (
    STATIC_FOLDER,
    TEMPLATE_FOLDER,
    load_dotenv,
    secret_key,
    session_config,
)
from quiz_data import assert_quiz_integrity
from routes import register_routes


def create_app() -> Flask:
    load_dotenv()
    assert_quiz_integrity()

    app = Flask(
        __name__,
        template_folder=TEMPLATE_FOLDER,
        static_folder=STATIC_FOLDER,
        static_url_path="/static",
    )
    app.secret_key = secret_key()
    app.config.update(session_config())

    register_routes(app)
    return app
