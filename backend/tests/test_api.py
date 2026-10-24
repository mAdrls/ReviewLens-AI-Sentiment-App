import pytest
import sys
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_api_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["storage"] == "Local JSON / No-Database Persistence"

def test_get_products(client):
    response = client.get("/api/products")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["count"] >= 5
    assert len(data["data"]) >= 5
    first = data["data"][0]
    assert "name" in first
    assert "stats" in first
    assert "positive_pct" in first["stats"]

def test_get_product_detail_success(client):
    response = client.get("/api/products/prod-1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["data"]["id"] == "prod-1"
    assert "SoundWave" in data["data"]["name"]
    assert "stats" in data["data"]
    assert "summary_text" in data["data"]

def test_get_product_detail_not_found(client):
    response = client.get("/api/products/non-existent-999")
    assert response.status_code == 404
    data = response.get_json()
    assert data["status"] == "not_found"

def test_get_product_reviews(client):
    response = client.get("/api/products/prod-1/reviews")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["count"] > 0
    assert len(data["data"]) > 0
    first_review = data["data"][0]
    assert "predicted_sentiment" in first_review
    assert "confidence_pct" in first_review

def test_get_product_reviews_filtered(client):
    response = client.get("/api/products/prod-1/reviews?sentiment=positive")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    for r in data["data"]:
        assert r["predicted_sentiment"] == "positive"

def test_analyze_valid_positive_review(client):
    payload = {"review": "The sound quality is absolutely exceptional and battery life is superb!"}
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    res = data["data"]
    assert res["sentiment"] == "positive"
    assert "confidence_pct" in res
    assert "probabilities" in res
    assert "keywords" in res
    assert len(res["keywords"]) > 0

def test_analyze_valid_negative_review(client):
    payload = {"review": "Terrible build quality. Broke after two days and customer support was horrible."}
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    res = data["data"]
    assert res["sentiment"] == "negative"

def test_analyze_empty_review(client):
    response = client.post("/api/analyze", json={"review": ""})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_analyze_missing_payload(client):
    response = client.post("/api/analyze", json={})
    assert response.status_code == 400

def test_analytics_overview(client):
    response = client.get("/api/analytics/overview")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    res = data["data"]
    assert res["total_products"] >= 5
    assert res["total_reviews"] > 0
    assert "sentiment_counts" in res
    assert "sentiment_percentages" in res
    assert res["sentiment_percentages"]["positive"] >= 0
    assert "best_product" in res

def test_analytics_products(client):
    response = client.get("/api/analytics/products")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert len(data["data"]) >= 5

def test_model_info(client):
    response = client.get("/api/model/info")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "metrics" in data["data"]
    assert "architecture" in data["data"]
    assert data["data"]["metrics"]["accuracy"] > 0

def test_session_history(client):
    # Perform an analysis first
    client.post("/api/analyze", json={"review": "Great quality and fast delivery."})
    response = client.get("/api/history")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["count"] > 0
