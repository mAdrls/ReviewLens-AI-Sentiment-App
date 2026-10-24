from flask import Flask
from routes.analysis import analysis_bp
from routes.products import products_bp
from routes.analytics import analytics_bp

def register_blueprints(app: Flask):
    """Register all API route blueprints on the Flask application."""
    app.register_blueprint(analysis_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(analytics_bp)
