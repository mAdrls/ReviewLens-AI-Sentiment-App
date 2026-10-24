import pytest
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from services.sentiment_service import sentiment_service

def test_sentiment_service_ready():
    assert sentiment_service.is_ready() is True

def test_sentiment_prediction_positive():
    text = "The audio clarity is brilliant and battery life is outstanding!"
    result = sentiment_service.analyze_text(text)
    assert result["sentiment"] == "positive"
    # In a 3-class model, positive should have highest probability
    assert result["probabilities"]["positive"] >= result["probabilities"]["negative"]
    assert result["probabilities"]["positive"] >= result["probabilities"]["neutral"]
    assert len(result["keywords"]) > 0

def test_sentiment_prediction_negative():
    text = "Horrible product. Stopped working after two days and customer support was completely useless."
    result = sentiment_service.analyze_text(text)
    assert result["sentiment"] == "negative"
    assert result["probabilities"]["negative"] > result["probabilities"]["positive"]

def test_probability_distribution_sums_to_one():
    text = "Pretty average build, works fine for the basic price."
    result = sentiment_service.analyze_text(text)
    probs = result["probabilities"]
    total = sum(probs.values())
    assert pytest.approx(total, 0.05) == 1.0

def test_keyword_attributions():
    text = "Outstanding build quality and fast charging."
    result = sentiment_service.analyze_text(text)
    assert "keyword_details" in result
    details = result["keyword_details"]
    assert len(details) > 0
    first_term = details[0]
    assert "term" in first_term
    assert "score" in first_term
