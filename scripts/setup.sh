#!/usr/bin/env bash
# ReviewLens AI - Linux / macOS Setup & Run Script
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "=========================================================="
echo "         ReviewLens AI - Quick Setup & Launch            "
echo "=========================================================="

echo "[1/4] Checking Python..."
command -v python3 >/dev/null 2>&1 || { echo >&2 "Python 3 is required but not installed."; exit 1; }

echo "[2/4] Installing backend dependencies..."
python3 -m pip install -r backend/requirements.txt

echo "[3/4] Training Sentiment Analysis Model..."
python3 backend/ml/train_model.py

echo "[4/4] Starting Flask REST API and Web App..."
echo "Application is live at: http://127.0.0.1:5000"
echo "Press Ctrl+C to stop the server."

python3 backend/app.py
