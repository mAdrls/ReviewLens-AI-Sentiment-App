from flask import Blueprint, jsonify
from services.analytics_service import analytics_service
from services.sentiment_service import sentiment_service
from config import APP_NAME, APP_VERSION

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api")

@analytics_bp.route("/health", methods=["GET"])
def health_check():
    """Verify application health and model pipeline readiness."""
    model_ready = sentiment_service.is_ready()
    return jsonify({
        "status": "healthy" if model_ready else "degraded",
        "app": APP_NAME,
        "version": APP_VERSION,
        "model_loaded": model_ready,
        "storage": "Local JSON / No-Database Persistence"
    }), 200 if model_ready else 503

@analytics_bp.route("/analytics/overview", methods=["GET"])
def get_overview_analytics():
    """Return aggregated platform metrics and sentiment distributions."""
    try:
        overview = analytics_service.get_overview()
        return jsonify({
            "status": "success",
            "data": overview
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to compute overview analytics: {str(e)}"}), 500

@analytics_bp.route("/analytics/products", methods=["GET"])
def get_product_analytics():
    """Return comparative metrics across all predefined products."""
    try:
        comparisons = analytics_service.get_product_comparisons()
        return jsonify({
            "status": "success",
            "count": len(comparisons),
            "data": comparisons
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to compute product comparisons: {str(e)}"}), 500

@analytics_bp.route("/model/info", methods=["GET"])
def get_model_information():
    """Return model architecture, training details, actual test evaluation, and limitations."""
    info = sentiment_service.get_model_info()
    return jsonify({
        "status": "success",
        "data": info
    }), 200
