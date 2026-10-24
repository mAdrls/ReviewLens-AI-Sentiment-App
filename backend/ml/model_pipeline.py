import re
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

def preprocess_text(text: str) -> str:
    """Clean text by lowercasing, normalizing whitespace, and removing special characters."""
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    # Replace URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    # Remove HTML tags if any
    text = re.sub(r'<.*?>', '', text)
    # Remove excessive punctuation repetitions but keep basic words
    text = re.sub(r'[^a-zA-Z0-9\s\']', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def build_pipeline() -> Pipeline:
    """Create the TF-IDF + Logistic Regression classification pipeline."""
    return Pipeline([
        ('tfidf', TfidfVectorizer(
            preprocessor=preprocess_text,
            ngram_range=(1, 2),
            stop_words='english',
            min_df=1,
            sublinear_tf=True
        )),
        ('clf', LogisticRegression(
            C=2.5,
            max_iter=500,
            solver='lbfgs',
            random_state=42
        ))
    ])

def explain_prediction(pipeline: Pipeline, raw_text: str, top_k: int = 5):
    """
    Extract keyword contributions and feature attributions for the input text.
    Uses TF-IDF weights multiplied by the classifier's class-specific coefficients.
    """
    tfidf = pipeline.named_steps['tfidf']
    clf = pipeline.named_steps['clf']
    
    cleaned = preprocess_text(raw_text)
    if not cleaned:
        return []
    
    # Transform text to tfidf vector
    tfidf_vec = tfidf.transform([cleaned])
    if tfidf_vec.nnz == 0:
        return []
    
    feature_names = tfidf.get_feature_names_out()
    classes = list(clf.classes_)
    probs = clf.predict_proba(tfidf_vec)[0]
    predicted_idx = int(np.argmax(probs))
    predicted_class = classes[predicted_idx]
    
    # Get coefficients for the predicted class
    if len(classes) == 2:
        coefs = clf.coef_[0] if predicted_idx == 1 else -clf.coef_[0]
    else:
        coefs = clf.coef_[predicted_idx]
        
    non_zero_indices = tfidf_vec.indices
    non_zero_values = tfidf_vec.data
    
    contributions = []
    for idx, tfidf_val in zip(non_zero_indices, non_zero_values):
        feat_name = feature_names[idx]
        weight = coefs[idx]
        score = tfidf_val * weight
        contributions.append({
            "term": feat_name,
            "score": round(float(score), 4),
            "tfidf": round(float(tfidf_val), 4),
            "importance": round(abs(float(score)), 4)
        })
        
    # Sort by positive contribution to the predicted class
    contributions.sort(key=lambda x: x["score"], reverse=True)
    return contributions[:top_k]
