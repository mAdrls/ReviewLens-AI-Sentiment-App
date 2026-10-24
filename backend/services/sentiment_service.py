import os
import json
import joblib
from datetime import datetime
from typing import Dict, Any, List

from config import MODEL_FILE, METRICS_FILE
from ml.model_pipeline import explain_prediction, preprocess_text

# In-memory history for user-submitted analyses in current session
_ANALYSIS_HISTORY: List[Dict[str, Any]] = []

class SentimentService:
    def __init__(self):
        self.pipeline = None
        self.metrics = {}
        self.load_model()

    def load_model(self):
        """Load the trained sentiment analysis pipeline and metrics."""
        if os.path.exists(MODEL_FILE):
            self.pipeline = joblib.load(MODEL_FILE)
        else:
            self.pipeline = None

        if os.path.exists(METRICS_FILE):
            with open(METRICS_FILE, "r", encoding="utf-8") as f:
                self.metrics = json.load(f)
        else:
            self.metrics = {}

    def is_ready(self) -> bool:
        return self.pipeline is not None

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze a review text and return prediction, confidence, keywords, and explanation."""
        if not self.is_ready():
            raise RuntimeError("Sentiment model artifact is not loaded. Please train the model first.")

        if not text or not isinstance(text, str) or not text.strip():
            raise ValueError("Review text cannot be empty or blank.")

        cleaned = preprocess_text(text)
        if not cleaned:
            # All punctuation or non-alphanumeric
            return {
                "sentiment": "neutral",
                "confidence": 0.50,
                "confidence_pct": 50.0,
                "confidence_level": "Low",
                "probabilities": {"positive": 0.33, "neutral": 0.34, "negative": 0.33},
                "keywords": [],
                "explanation": "No distinctive vocabulary detected in input; assigned neutral baseline.",
                "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        # Predict probabilities
        classes = list(self.pipeline.named_steps['clf'].classes_)
        raw_probs = self.pipeline.predict_proba([cleaned])[0]
        
        prob_dict = {cls: round(float(p), 4) for cls, p in zip(classes, raw_probs)}
        
        # Determine highest probability class
        pred_label = self.pipeline.predict([cleaned])[0]
        max_prob = prob_dict[pred_label]
        conf_pct = round(max_prob * 100, 1)

        if conf_pct >= 75.0:
            conf_level = "High"
        elif conf_pct >= 55.0:
            conf_level = "Moderate"
        else:
            conf_level = "Low"

        # Keyword contributions
        top_terms = explain_prediction(self.pipeline, text, top_k=5)
        keywords = [t["term"] for t in top_terms]

        # Generate explanatory insight
        if top_terms:
            key_words_str = ", ".join([f"'{t['term']}'" for t in top_terms[:3]])
            explanation = (
                f"Classified as {pred_label.upper()} ({conf_pct}% estimated probability) "
                f"based primarily on keyword signals including {key_words_str}."
            )
        else:
            explanation = (
                f"Classified as {pred_label.upper()} ({conf_pct}% estimated probability) "
                f"based on general sentence structure and background n-gram patterns."
            )

        result = {
            "text": text,
            "sentiment": pred_label,
            "confidence": max_prob,
            "confidence_pct": conf_pct,
            "confidence_level": conf_level,
            "probabilities": prob_dict,
            "keywords": keywords,
            "keyword_details": top_terms,
            "explanation": explanation,
            "model_identifier": "reviewlens_tfidf_logreg_v1",
            "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Save to session history (capped at 20 items)
        _ANALYSIS_HISTORY.insert(0, {
            "text": text if len(text) <= 90 else text[:87] + "...",
            "sentiment": pred_label,
            "confidence_pct": conf_pct,
            "analyzed_at": result["analyzed_at"]
        })
        if len(_ANALYSIS_HISTORY) > 20:
            _ANALYSIS_HISTORY.pop()

        return result

    def get_history(self) -> List[Dict[str, Any]]:
        return _ANALYSIS_HISTORY

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "is_ready": self.is_ready(),
            "metrics": self.metrics,
            "architecture": {
                "name": "ReviewLens AI Pipeline",
                "vectorizer": "TF-IDF Vectorizer (ngram_range=(1, 2), sublinear_tf=True)",
                "classifier": "Logistic Regression (Multinomial, L2, C=2.5)",
                "classes": ["negative", "neutral", "positive"],
                "preprocessing": "Lowercasing, regex tokenization, punctuation removal, English stopword filtration"
            }
        }

# Global singleton service
sentiment_service = SentimentService()
