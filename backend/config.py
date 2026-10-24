import os
from pathlib import Path

# Paths configuration
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
DATA_DIR = BACKEND_DIR / "data"
MODEL_DIR = BACKEND_DIR / "models"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

PRODUCTS_FILE = DATA_DIR / "products.json"
REVIEWS_FILE = DATA_DIR / "reviews.json"
TRAINING_FILE = DATA_DIR / "training_reviews.csv"
MODEL_FILE = MODEL_DIR / "sentiment_pipeline.joblib"
METRICS_FILE = MODEL_DIR / "metrics.json"

# Application config
APP_NAME = "ReviewLens AI"
APP_VERSION = "1.0.0"
HOST = "127.0.0.1"
PORT = 5000
DEBUG = True
