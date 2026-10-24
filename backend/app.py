import os
import sys
from pathlib import Path
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from config import FRONTEND_DIR, HOST, PORT, DEBUG, APP_NAME
from routes import register_blueprints

def create_app() -> Flask:
    app = Flask(
        __name__,
        static_folder=str(FRONTEND_DIR),
        static_url_path=""
    )

    # Enable CORS for all routes (allows standalone frontend servers like Vite or Live Server)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register API blueprints
    register_blueprints(app)

    # Serve Frontend UI routes
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        """Serve frontend static files and SPA HTML pages."""
        target = os.path.join(str(FRONTEND_DIR), path)
        if path != "" and os.path.isfile(target):
            return send_from_directory(str(FRONTEND_DIR), path)
        else:
            return send_from_directory(str(FRONTEND_DIR), "index.html")

    # Global 404 handler for API routes
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "error": "The requested resource or endpoint was not found.",
            "status": "not_found"
        }), 404

    # Global 500 handler
    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({
            "error": "Internal server error. Check server logs for details.",
            "status": "server_error"
        }), 500

    return app

app = create_app()

if __name__ == "__main__":
    print("=" * 60)
    print(f"[*] Starting {APP_NAME} Server")
    print(f"[+] Local Web App URL: http://{HOST}:{PORT}")
    print(f"[+] API Health URL:    http://{HOST}:{PORT}/api/health")
    print("=" * 60)
    app.run(host=HOST, port=PORT, debug=DEBUG)
