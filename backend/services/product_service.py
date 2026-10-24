import json
import os
from collections import Counter
from typing import List, Dict, Any, Optional

from config import PRODUCTS_FILE, REVIEWS_FILE
from services.sentiment_service import sentiment_service

class ProductService:
    def __init__(self):
        self._products: List[Dict[str, Any]] = []
        self._reviews: List[Dict[str, Any]] = []
        self._enriched_reviews: List[Dict[str, Any]] = []
        self.load_data()

    def load_data(self):
        """Load products and reviews from local JSON files."""
        if os.path.exists(PRODUCTS_FILE):
            with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
                self._products = json.load(f)
        else:
            self._products = []

        if os.path.exists(REVIEWS_FILE):
            with open(REVIEWS_FILE, "r", encoding="utf-8") as f:
                self._reviews = json.load(f)
        else:
            self._reviews = []

        self._enrich_all_reviews()

    def _enrich_all_reviews(self):
        """Run ML sentiment analysis across all sample reviews and cache results."""
        self._enriched_reviews = []
        for r in self._reviews:
            rev_copy = dict(r)
            if sentiment_service.is_ready():
                try:
                    pred = sentiment_service.analyze_text(r["text"])
                    rev_copy["predicted_sentiment"] = pred["sentiment"]
                    rev_copy["confidence_pct"] = pred["confidence_pct"]
                    rev_copy["confidence_level"] = pred["confidence_level"]
                    rev_copy["probabilities"] = pred["probabilities"]
                    rev_copy["keywords"] = pred["keywords"]
                except Exception:
                    rev_copy["predicted_sentiment"] = "neutral"
                    rev_copy["confidence_pct"] = 50.0
                    rev_copy["confidence_level"] = "Low"
                    rev_copy["probabilities"] = {"positive": 0.33, "neutral": 0.34, "negative": 0.33}
                    rev_copy["keywords"] = []
            else:
                rev_copy["predicted_sentiment"] = "neutral"
                rev_copy["confidence_pct"] = 50.0
                rev_copy["confidence_level"] = "Low"
                rev_copy["probabilities"] = {"positive": 0.33, "neutral": 0.34, "negative": 0.33}
                rev_copy["keywords"] = []
            self._enriched_reviews.append(rev_copy)

    def get_all_products(self) -> List[Dict[str, Any]]:
        """Return all products augmented with calculated sentiment analytics."""
        result = []
        for p in self._products:
            prod_summary = self.get_product_summary(p["id"])
            p_aug = dict(p)
            p_aug["stats"] = prod_summary["stats"]
            p_aug["review_count"] = prod_summary["review_count"]
            p_aug["sentiment_score"] = prod_summary["sentiment_score"]
            result.append(p_aug)
        return result

    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Return a single product by ID."""
        for p in self._products:
            if p["id"] == product_id:
                prod_summary = self.get_product_summary(p["id"])
                p_aug = dict(p)
                p_aug["stats"] = prod_summary["stats"]
                p_aug["review_count"] = prod_summary["review_count"]
                p_aug["sentiment_score"] = prod_summary["sentiment_score"]
                p_aug["top_positive_keywords"] = prod_summary["top_positive_keywords"]
                p_aug["top_negative_keywords"] = prod_summary["top_negative_keywords"]
                p_aug["summary_text"] = prod_summary["summary_text"]
                return p_aug
        return None

    def get_product_reviews(self, product_id: str, sentiment_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return all enriched reviews for a given product with optional sentiment filter."""
        filtered = [r for r in self._enriched_reviews if r["product_id"] == product_id]
        if sentiment_filter and sentiment_filter.lower() in ["positive", "negative", "neutral"]:
            filtered = [r for r in filtered if r["predicted_sentiment"] == sentiment_filter.lower()]
        return filtered

    def get_product_summary(self, product_id: str) -> Dict[str, Any]:
        """Compute complete statistics and keywords for a product."""
        reviews = [r for r in self._enriched_reviews if r["product_id"] == product_id]
        total = len(reviews)
        if total == 0:
            return {
                "product_id": product_id,
                "review_count": 0,
                "sentiment_score": 50.0,
                "stats": {
                    "positive_count": 0, "negative_count": 0, "neutral_count": 0,
                    "positive_pct": 0.0, "negative_pct": 0.0, "neutral_pct": 0.0
                },
                "top_positive_keywords": [],
                "top_negative_keywords": [],
                "summary_text": "No reviews available yet for this product."
            }

        counts = Counter(r["predicted_sentiment"] for r in reviews)
        pos = counts["positive"]
        neg = counts["negative"]
        neu = counts["neutral"]

        pos_pct = round((pos / total) * 100, 1)
        neg_pct = round((neg / total) * 100, 1)
        neu_pct = round((neu / total) * 100, 1)

        # Net sentiment index: (positive - negative) mapped from [-1, 1] to [0, 100]
        net_score = round(50.0 + ((pos - neg) / total) * 50.0, 1)

        # Keywords accumulation
        pos_words = Counter()
        neg_words = Counter()
        for r in reviews:
            kws = r.get("keywords", [])
            if r["predicted_sentiment"] == "positive":
                pos_words.update(kws)
            elif r["predicted_sentiment"] == "negative":
                neg_words.update(kws)

        top_pos = [w for w, _ in pos_words.most_common(6)]
        top_neg = [w for w, _ in neg_words.most_common(6)]

        # Generate insightful summary statement
        if pos_pct >= 60:
            sentiment_tone = "predominantly favorable customer feedback"
        elif neg_pct >= 40:
            sentiment_tone = "notable customer friction and recurring complaints"
        else:
            sentiment_tone = "balanced user feedback with mixed impressions"

        summary_text = (
            f"Based on {total} sample reviews analyzed by ReviewLens AI, this product demonstrates "
            f"{sentiment_tone} ({pos_pct}% positive vs. {neg_pct}% negative). "
        )
        if top_pos:
            summary_text += f"Key praise highlights include {', '.join(top_pos[:3])}. "
        if top_neg:
            summary_text += f"Primary areas flagged for improvement cite {', '.join(top_neg[:3])}."

        return {
            "product_id": product_id,
            "review_count": total,
            "sentiment_score": net_score,
            "stats": {
                "positive_count": pos,
                "negative_count": neg,
                "neutral_count": neu,
                "positive_pct": pos_pct,
                "negative_pct": neg_pct,
                "neutral_pct": neu_pct
            },
            "top_positive_keywords": top_pos,
            "top_negative_keywords": top_neg,
            "summary_text": summary_text
        }

# Global singleton product service
product_service = ProductService()
