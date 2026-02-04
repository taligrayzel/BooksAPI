"""Centralized error handlers and response helpers."""
from flask import Flask, g, jsonify


def _error_response(e, default: str, status: int):
    msg = getattr(e, "description", None) or default
    return jsonify(error=str(msg) if msg else default), status


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(400)
    def bad_request(e):
        return _error_response(e, "Bad request", 400)

    @app.errorhandler(401)
    def unauthorized(e):
        return _error_response(e, "Unauthorized", 401)

    @app.errorhandler(403)
    def forbidden(e):
        return _error_response(e, "Forbidden", 403)

    @app.errorhandler(404)
    def not_found(e):
        return _error_response(e, "Resource not found", 404)

    @app.errorhandler(405)
    def method_not_allowed(e):
        return _error_response(e, "Method not allowed", 405)

    @app.errorhandler(408)
    def request_timeout(e):
        return _error_response(e, "Request timeout", 408)

    @app.errorhandler(409)
    def conflict(e):
        return _error_response(e, "Conflict", 409)

    @app.errorhandler(422)
    def unprocessable_entity(e):
        return _error_response(e, "Unprocessable entity", 422)

    @app.errorhandler(429)
    def too_many_requests(e):
        return _error_response(e, "Too many requests", 429)

    @app.errorhandler(500)
    def internal_error(e):
        return _error_response(e, "Internal server error", 500)

    @app.errorhandler(503)
    def service_unavailable(e):
        return _error_response(e, "Service unavailable", 503)

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        app.logger.exception(
            "Unhandled exception id=%s: %s",
            getattr(g, "request_id", "-"),
            e,
        )
        return jsonify(error="Internal server error"), 500
