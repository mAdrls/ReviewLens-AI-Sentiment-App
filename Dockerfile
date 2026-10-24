FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy application files
COPY . .

# Train model
RUN python backend/ml/train_model.py

# Expose port
EXPOSE 5000

# Start Flask application
CMD ["python", "backend/app.py"]
