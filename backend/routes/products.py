from flask import Blueprint, request, jsonify
from services.product_service import product_service

products_bp = Blueprint("products", __name__, url_prefix="/api")

@products_bp.route("/products", methods=["GET"])
def list_products():
    """Return all products with pre-calculated sentiment statistics."""
    try:
        products = product_service.get_all_products()
        return jsonify({
            "status": "success",
            "count": len(products),
            "data": products
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve products: {str(e)}"}), 500

@products_bp.route("/products/<product_id>", methods=["GET"])
def get_product(product_id):
    """Return detailed metadata, sentiment scores, and summaries for a specific product."""
    product = product_service.get_product(product_id)
    if not product:
        return jsonify({
            "error": f"Product with ID '{product_id}' was not found in catalog.",
            "status": "not_found"
        }), 404

    return jsonify({
        "status": "success",
        "data": product
    }), 200

@products_bp.route("/products/<product_id>/reviews", methods=["GET"])
def get_product_reviews(product_id):
    """Return enriched sample reviews for a specific product with optional sentiment filter."""
    product = product_service.get_product(product_id)
    if not product:
        return jsonify({
            "error": f"Product with ID '{product_id}' was not found in catalog.",
            "status": "not_found"
        }), 404

    sentiment_filter = request.args.get("sentiment")
    reviews = product_service.get_product_reviews(product_id, sentiment_filter=sentiment_filter)

    return jsonify({
        "status": "success",
        "product_id": product_id,
        "product_name": product["name"],
        "filter_applied": sentiment_filter if sentiment_filter else "all",
        "count": len(reviews),
        "data": reviews
    }), 200
