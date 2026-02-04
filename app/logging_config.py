"""Application-wide logging and request logging."""
import logging
import time
from uuid import uuid4

from flask import Flask, g, request


def configure_logging(app: Flask) -> None:
    """Configure application-wide logging."""
    if not app.logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        )
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)

    app.logger.setLevel(logging.INFO)


def register_request_logging(app: Flask) -> None:
    """Add hooks to log every request and response."""

    @app.before_request
    def _log_request():
        g.request_id = str(uuid4())
        g.request_started_at = time.time()

        app.logger.info(
            "Incoming request id=%s method=%s path=%s remote_addr=%s user_agent=%s",
            g.request_id,
            request.method,
            request.full_path.rstrip("?"),
            request.remote_addr,
            request.headers.get("User-Agent", "-"),
        )

    @app.after_request
    def _log_response(response):
        started_at = getattr(g, "request_started_at", None)
        duration_ms = (time.time() - started_at) * 1000 if started_at else None

        app.logger.info(
            "Completed request id=%s method=%s path=%s status=%s duration_ms=%s",
            getattr(g, "request_id", "-"),
            request.method,
            request.full_path.rstrip("?"),
            response.status_code,
            f"{duration_ms:.2f}" if duration_ms is not None else "unknown",
        )

        response.headers.setdefault("X-Request-ID", getattr(g, "request_id", "-"))
        return response
