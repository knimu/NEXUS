"""
NEXUS Member 4 Flask Application Initialization.
Provides Flask app factory for Investigation Dashboard & REST APIs.
"""

import os
import sys

# Ensure repository root directory is in sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from flask import Flask
from app.routes import main_bp


def create_app() -> Flask:
    """Create and configure Flask application instance."""
    app = Flask(__name__)
    app.register_blueprint(main_bp)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
