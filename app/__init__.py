"""
NEXUS Member 4 Flask Application Initialization.
Provides Flask app factory for Investigation Dashboard & REST APIs.
"""

from flask import Flask
from app.routes import main_bp


def create_app() -> Flask:
    """Create and configure Flask application instance."""
    app = Flask(__name__)

    # Register blueprints
    app.register_blueprint(main_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
