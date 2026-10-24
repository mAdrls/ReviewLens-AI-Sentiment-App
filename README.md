# ReviewLens AI - Product Review Sentiment Analysis Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1+-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Scikit--Learn](https://img.shields.io/badge/Scikit--Learn-1.6+-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat-square&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.4-FF6384?style=flat-square&logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)

**ReviewLens AI** is a complete, full-stack, database-free **Product Review Sentiment Analysis Web Application** designed for academic demonstrations and portfolio presentation. It integrates a real Python Machine Learning NLP pipeline with a modern, high-performance SaaS analytics dashboard.

---

## 🌟 Key Features

1. **Zero Database Infrastructure:**
   - Preloaded sample catalog of 5 consumer products and ~60 labeled sample reviews stored in clean JSON files.
   - Session-based in-memory history for live ad-hoc predictions that automatically resets on server restarts.
   - Zero PostgreSQL, MySQL, Redis, or Celery requirements.

2. **Real Machine Learning Pipeline (Explainable AI):**
   - Natural Language Processing (NLP) pipeline built with **Scikit-learn**:
     - Text cleaning & preprocessing (regex tokenization, punctuation removal, English stopword filtration).
     - Sublinear **TF-IDF Vectorizer** (unigrams + bigrams).
     - **Multinomial Logistic Regression** with L2 penalty and L-BFGS optimization.
   - Generates calibrated probability distributions for **Positive**, **Neutral**, and **Negative** classes.
   - **Feature Attribution:** Extracts top-contributing n-gram tokens and explains the prediction reasoning.

3. **Modern SaaS Analytics Dashboard:**
   - Dark charcoal sidebar (`#0f172a`) with light neutral workspace (`#f8fafc`).
   - Dynamic KPI cards displaying total reviews, positive %, neutral %, and negative % calculated dynamically from local data.
   - Highlights the highest customer satisfaction product and product needing improvement.
   - Interactive **Chart.js** charts:
     - Overall sentiment distribution doughnut chart.
     - Product-by-product comparison bar chart.
     - Product-level sentiment breakdown charts.

4. **Product Explorer & Deep-Dive:**
   - Browse predefined products (SoundWave Headphones, AeroPulse Watch, Nova Smartphone, TitanBook Laptop, BoomEcho Speaker).
   - View detailed sentiment metrics, automated AI summaries, and common positive/negative keyword drivers.
   - Filter customer reviews by sentiment (All, Positive, Neutral, Negative).

5. **Live Review Sentiment Analyzer:**
   - Textarea with character counter and quick clickable demonstration examples.
   - Evaluates custom text in real-time with confidence scores, probability meters, keyword badges, and human-readable explanations.

6. **Model Transparency & Evaluation Page:**
   - Displays actual holdout validation metrics (Precision, Recall, F1-Score).
   - Visual confusion matrix heatmap.
   - Pipeline architecture flow and realistic academic limitations.

---

## 📂 Project Structure

```text
reviewlens-ai/
├── backend/
│   ├── app.py                     # Flask application entry point & static server
│   ├── config.py                  # Absolute paths and configuration settings
│   ├── requirements.txt           # Python backend dependencies
│   ├── data/
│   │   ├── products.json          # Predefined catalog of 5 products
│   │   ├── reviews.json           # Sample customer reviews per product
│   │   └── training_reviews.csv   # 100 labeled training sentences
│   ├── ml/
│   │   ├── model_pipeline.py      # TF-IDF + Logistic Regression pipeline & XAI
│   │   └── train_model.py         # Model training & holdout evaluation script
│   ├── models/
│   │   ├── sentiment_pipeline.joblib  # Serialized trained ML pipeline
│   │   └── metrics.json           # Evaluation metrics & confusion matrix
│   ├── routes/
│   │   ├── __init__.py            # Blueprint registration
│   │   ├── analysis.py            # POST /api/analyze & GET /api/history
│   │   ├── analytics.py           # GET /api/analytics/* & GET /api/model/info
│   │   └── products.py            # GET /api/products/*
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analytics_service.py   # Aggregated analytics logic
│   │   ├── product_service.py     # Product enrichment & keyword aggregation
│   │   └── sentiment_service.py   # ML inference & XAI explanation service
│   └── tests/
│       ├── test_api.py            # 14 Flask API integration tests
│       └── test_sentiment.py      # 5 ML pipeline & prediction tests
├── frontend/
│   ├── index.html                 # Single-page dashboard application
│   ├── css/
│   │   └── styles.css             # SaaS theme styles & responsive layout
│   └── js/
│       ├── api.js                 # API client wrapper
│       ├── app.js                 # Routing, UI controllers & state management
│       └── charts.js              # Chart.js visualizations
├── scripts/
│   ├── setup.ps1                  # One-click Windows PowerShell setup script
│   └── setup.sh                   # Linux / macOS setup script
├── .env.example
├── .gitignore
├── Dockerfile
└── README.md
```

---

## 🚀 Quick Setup & Execution (Windows)

### Option 1: One-Click Setup Script (PowerShell)

Open PowerShell in the `reviewlens-ai` folder and run:

```powershell
.\scripts\setup.ps1
```

### Option 2: Step-by-Step Manual Setup

1. **Navigate to the project root:**
   ```powershell
   cd "C:\Users\Kartik Singh\.gemini\antigravity\scratch\reviewlens-ai"
   ```

2. **(Optional) Create and activate a virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r backend/requirements.txt
   ```

4. **Train the ML model (generates `backend/models/sentiment_pipeline.joblib`):**
   ```powershell
   python backend/ml/train_model.py
   ```

5. **Start the Flask web application:**
   ```powershell
   python backend/app.py
   ```

6. **Open your browser and navigate to:**
   ```
   http://127.0.0.1:5000
   ```

---

## 🧪 Automated Testing

ReviewLens AI comes with 19 comprehensive automated tests verifying API endpoints, error handling, and ML inference.

To run the test suite:

```powershell
pytest backend/tests -v
```

All 19 tests will execute and pass:
- API health check (`/api/health`)
- Product catalog retrieval (`/api/products`)
- Product detail retrieval (`/api/products/<id>`)
- 404 response on non-existent product ID
- Product review enrichment & sentiment filtering
- Real-time prediction on positive review
- Real-time prediction on negative review
- Rejection of empty or invalid reviews (HTTP 400)
- Global analytics calculation (`/api/analytics/overview`)
- Product comparison data for charts
- Model evaluation metrics (`/api/model/info`)
- In-memory session history
- Probability distribution normalization (sums to 1.0)
- Feature keyword attribution extraction

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health check & model readiness |
| `GET` | `/api/products` | Retrieve all 5 predefined products with calculated stats |
| `GET` | `/api/products/<id>` | Retrieve detailed metadata for a single product |
| `GET` | `/api/products/<id>/reviews` | Retrieve sample reviews (supports `?sentiment=positive\|negative\|neutral`) |
| `POST` | `/api/analyze` | Classify custom review text with ML pipeline & return XAI metrics |
| `GET` | `/api/analytics/overview` | Aggregated dashboard KPIs and highlights |
| `GET` | `/api/analytics/products` | Product-by-product comparison series for Chart.js |
| `GET` | `/api/model/info` | Architecture specs, training info, and holdout evaluation metrics |
| `GET` | `/api/history` | Retrieve in-memory analyses evaluated in the current session |

### Sample POST `/api/analyze` Request

```json
{
  "review": "The active noise cancellation is remarkable and battery easily lasts 40 hours!"
}
```

### Sample Response

```json
{
  "status": "success",
  "data": {
    "sentiment": "positive",
    "confidence": 0.7842,
    "confidence_pct": 78.4,
    "confidence_level": "High",
    "probabilities": {
      "positive": 0.7842,
      "neutral": 0.1423,
      "negative": 0.0735
    },
    "keywords": ["noise cancellation", "remarkable", "battery"],
    "explanation": "Classified as POSITIVE (78.4% estimated probability) based primarily on keyword signals including 'noise cancellation', 'remarkable', 'battery'.",
    "model_identifier": "reviewlens_tfidf_logreg_v1"
  }
}
```

---

## 🎓 College Demonstration Guide

When presenting this project to your professor or evaluator:

1. **Overview Dashboard:** Point out that all KPI numbers (Total Reviews, Positive %, Neutral %, Negative %) and Chart.js graphs are calculated dynamically from local sample reviews and the model's actual predictions.
2. **Product Catalog:** Open the *Product Explorer*, select *SoundWave Pro ANC Headphones*, and show the *Automated AI Sentiment Summary* generated from the classified sample reviews.
3. **Sentiment Filtering:** Click the filter pills (*Positive*, *Neutral*, *Negative*) to show how customer reviews are categorized with individual sentiment badges.
4. **Live Review Analyzer:** 
   - Click one of the preloaded example chips to demonstrate instant classification.
   - Type a custom review (e.g. *"The screen is gorgeous but the battery died after three hours"*).
   - Point out the **Probability Distribution** and the **Contributing Tokens (Explainable AI)** chips showing *why* the model made its decision.
5. **Model Information:** Walk the teacher through the *Model & Metrics* page. Explain that the pipeline uses TF-IDF n-grams + Logistic Regression, and highlight the actual holdout evaluation table and confusion matrix.

---

## 🔒 Limitations & Future Work

- **Academic Dataset:** The demonstration model is trained on a curated 100-sample dataset of consumer electronics reviews. For enterprise deployment, the model can be retrained on 500,000+ Amazon or Yelp reviews simply by replacing `backend/data/training_reviews.csv`.
- **Sarcasm Detection:** As with most n-gram bag-of-words models, nuanced sarcasm or double negatives may occasionally be misclassified.
- **In-Memory History:** Review analyses submitted via the live analyzer are stored in memory for the active server session and intentionally not written to a permanent database.
