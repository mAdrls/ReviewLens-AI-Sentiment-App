from flask import Blueprint, request, jsonify
from services.sentiment_service import sentiment_service

analysis_bp = Blueprint("analysis", __name__, url_prefix="/api")

@analysis_bp.route("/analyze", methods=["POST"])
def analyze_review():
    """Accept review text, validate, execute ML pipeline, and return sentiment prediction."""
    if not request.is_json:
        return jsonify({
            "error": "Invalid request format. Content-Type must be application/json."
        }), 400

    data = request.get_json()
    if not data or "review" not in data:
        return jsonify({
            "error": "Missing required field 'review' in JSON payload."
        }), 400

    review_text = data.get("review")
    if not isinstance(review_text, str) or not review_text.strip():
        return jsonify({
            "error": "Review text cannot be empty or blank."
        }), 400

    if len(review_text) > 4000:
        return jsonify({
            "error": "Review text exceeds maximum allowed length of 4,000 characters."
        }), 400

    try:
        result = sentiment_service.analyze_text(review_text)
        return jsonify({
            "status": "success",
            "data": result
        }), 200
    except RuntimeError as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 503
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred during analysis: {str(e)}",
            "status": "error"
        }), 500

@analysis_bp.route("/history", methods=["GET"])
def get_session_history():
    """Return in-memory review analyses performed during the current server session."""
    history = sentiment_service.get_history()
    return jsonify({
        "status": "success",
        "count": len(history),
        "data": history,
        "note": "Temporary in-memory history. Resets upon server restart."
    }), 200
