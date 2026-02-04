"""Application factory and entry point."""
from dotenv import load_dotenv

load_dotenv()

from flask import Flask

from app.error_handlers import register_error_handlers
from app.logging_config import configure_logging, register_request_logging
from app.routers import register_blueprints


def create_app() -> Flask:
    flask_app = Flask(__name__)
    configure_logging(flask_app)
    register_request_logging(flask_app)
    register_error_handlers(flask_app)
    register_blueprints(flask_app)
    return flask_app


app = create_app()
