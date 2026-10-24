from collections import Counter
from typing import Dict, Any, List

from services.product_service import product_service
from services.sentiment_service import sentiment_service

class AnalyticsService:
    def get_overview(self) -> Dict[str, Any]:
        """Generate high-level metrics and dataset aggregations for the main dashboard."""
        all_products = product_service.get_all_products()
        all_reviews = product_service._enriched_reviews

        total_reviews = len(all_reviews)
        counts = Counter(r["predicted_sentiment"] for r in all_reviews)
        
        pos = counts["positive"]
        neg = counts["negative"]
        neu = counts["neutral"]

        pos_pct = round((pos / total_reviews * 100), 1) if total_reviews else 0.0
        neg_pct = round((neg / total_reviews * 100), 1) if total_reviews else 0.0
        neu_pct = round((neu / total_reviews * 100), 1) if total_reviews else 0.0

        # Find best performing and most critical product
        best_product = None
        worst_product = None
        if all_products:
            # Sort by positive_pct descending
            sorted_by_pos = sorted(all_products, key=lambda x: x["stats"]["positive_pct"], reverse=True)
            best_product = {
                "id": sorted_by_pos[0]["id"],
                "name": sorted_by_pos[0]["name"],
                "positive_pct": sorted_by_pos[0]["stats"]["positive_pct"],
                "sentiment_score": sorted_by_pos[0]["sentiment_score"]
            }
            # Sort by negative_pct descending
            sorted_by_neg = sorted(all_products, key=lambda x: x["stats"]["negative_pct"], reverse=True)
            worst_product = {
                "id": sorted_by_neg[0]["id"],
                "name": sorted_by_neg[0]["name"],
                "negative_pct": sorted_by_neg[0]["stats"]["negative_pct"],
                "sentiment_score": sorted_by_neg[0]["sentiment_score"]
            }

        recent_analyses = sentiment_service.get_history()

        return {
            "total_products": len(all_products),
            "total_reviews": total_reviews,
            "sentiment_counts": {
                "positive": pos,
                "negative": neg,
                "neutral": neu
            },
            "sentiment_percentages": {
                "positive": pos_pct,
                "negative": neg_pct,
                "neutral": neu_pct
            },
            "best_product": best_product,
            "worst_product": worst_product,
            "recent_analyses": recent_analyses[:5],
            "model_ready": sentiment_service.is_ready()
        }

    def get_product_comparisons(self) -> List[Dict[str, Any]]:
        """Return standardized comparison series for product charts."""
        products = product_service.get_all_products()
        comparisons = []
        for p in products:
            comparisons.append({
                "id": p["id"],
                "name": p["name"],
                "category": p["category"],
                "price": p["price"],
                "review_count": p["review_count"],
                "sentiment_score": p["sentiment_score"],
                "positive_pct": p["stats"]["positive_pct"],
                "negative_pct": p["stats"]["negative_pct"],
                "neutral_pct": p["stats"]["neutral_pct"],
                "positive_count": p["stats"]["positive_count"],
                "negative_count": p["stats"]["negative_count"],
                "neutral_count": p["stats"]["neutral_count"]
            })
        return comparisons

analytics_service = AnalyticsService()
