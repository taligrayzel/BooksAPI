"""API route blueprints."""
from app.routers.books import books_bp
from app.routers.authors import authors_bp
from app.routers.auth_routes import auth_bp
from app.routers.docs import docs_bp


def register_blueprints(app):
    app.register_blueprint(books_bp)
    app.register_blueprint(authors_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(docs_bp)
