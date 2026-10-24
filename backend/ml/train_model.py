import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib

# Ensure backend root is in sys.path
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from config import TRAINING_FILE, MODEL_FILE, METRICS_FILE, MODEL_DIR
from ml.model_pipeline import build_pipeline

def train_and_save():
    print("=" * 60)
    print("ReviewLens AI - Training Sentiment Analysis Model")
    print("=" * 60)

    if not os.path.exists(TRAINING_FILE):
        raise FileNotFoundError(f"Training dataset not found at: {TRAINING_FILE}")

    df = pd.read_csv(TRAINING_FILE)
    print(f"Loaded {len(df)} labeled training samples.")
    print("Class distribution:")
    print(df['label'].value_counts())

    X = df['text'].astype(str)
    y = df['label'].astype(str)

    # 1. Stratified hold-out split for honest evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    eval_pipeline = build_pipeline()
    eval_pipeline.fit(X_train, y_train)

    y_pred = eval_pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    labels = sorted(list(set(y)))
    cm = confusion_matrix(y_test, y_pred, labels=labels)

    print(f"\nModel Hold-Out Validation Accuracy: {acc * 100:.2f}%")
    print("\nClassification Report on Unseen Test Split:")
    print(classification_report(y_test, y_pred))

    # 2. Refit final deployment pipeline on full dataset for maximum vocabulary & capability
    final_pipeline = build_pipeline()
    final_pipeline.fit(X, y)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(final_pipeline, MODEL_FILE)
    print(f"\nFinal deployment model saved to: {MODEL_FILE}")

    vocab_size = len(final_pipeline.named_steps['tfidf'].vocabulary_)
    metrics_data = {
        "model_name": "TF-IDF + Multinomial Logistic Regression",
        "algorithm": "Multinomial Logistic Regression (L2 penalty, lbfgs)",
        "vectorizer": "TF-IDF (unigrams & bigrams, sublinear tf)",
        "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_samples": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "vocabulary_size": vocab_size,
        "classes": labels,
        "accuracy": round(float(acc), 4),
        "accuracy_pct": round(float(acc) * 100, 2),
        "classification_report": report,
        "confusion_matrix": {
            "labels": labels,
            "matrix": cm.tolist()
        },
        "hyperparameters": {
            "C": 2.5,
            "max_iter": 500,
            "solver": "lbfgs",
            "ngram_range": [1, 2],
            "sublinear_tf": True
        },
        "limitations": [
            "Trained on a compact academic demonstration dataset of consumer electronics reviews.",
            "Subtle sarcasm, irony, or double negatives may occasionally be misclassified.",
            "Domain-specific slang or regional colloquialisms not in vocabulary are mapped to neutral priors."
        ]
    }

    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)
    print(f"Model evaluation metrics saved to: {METRICS_FILE}")
    print("=" * 60)
    return metrics_data

if __name__ == "__main__":
    train_and_save()
