"""
Entry point for running Flask application via `python -m app`.
"""

import os
import sys

# Ensure repository root directory is in sys.path for robust module resolution
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from app import create_app

app = create_app()

if __name__ == "__main__":
    host = os.environ.get("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_RUN_PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")
    print(f"Starting NEXUS Investigation Dashboard server on http://{host}:{port}/ ...")
    app.run(host=host, port=port, debug=debug, use_reloader=False)
