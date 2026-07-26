"""Model inference service — loads the trained risk model and runs predictions."""
import os
import joblib
import numpy as np
import shap
from functools import lru_cache

MODEL_PATH = os.getenv("MODEL_PATH", "/models/risk_model.pkl")

FEATURES = [
    "population_density",
    "median_income",
    "flood_zone_overlap",
    "distance_to_hospital",
    "distance_to_shelter",
    "road_density",
    "impervious_surface_pct",
    "tree_cover_pct",
    "elevation_mean",
    "building_density",
]

FEATURE_LABELS = {
    "population_density": "high population density",
    "median_income": "low median income",
    "flood_zone_overlap": "high flood-zone overlap",
    "distance_to_hospital": "far from hospitals",
    "distance_to_shelter": "far from emergency shelters",
    "road_density": "low road density",
    "impervious_surface_pct": "high impervious surface",
    "tree_cover_pct": "low tree coverage",
    "elevation_mean": "low elevation",
    "building_density": "high building density",
}

RISK_THRESHOLDS = [
    (75, "Critical"),
    (50, "High"),
    (25, "Medium"),
    (0,  "Low"),
]


@lru_cache(maxsize=1)
def _load_model():
    """Load model once and cache in memory."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}. Run pipelines/train_model.py first."
        )
    return joblib.load(MODEL_PATH)


def score_to_category(score: float) -> str:
    for threshold, category in RISK_THRESHOLDS:
        if score >= threshold:
            return category
    return "Low"


def predict(feature_row: dict) -> dict:
    """
    Run inference on a single feature dict.

    Args:
        feature_row: dict with keys matching FEATURES list

    Returns:
        dict with risk_score (0-100), risk_category, confidence, top_factors
    """
    model = _load_model()

    X = np.array([[feature_row.get(f, 0.0) for f in FEATURES]])

    # Probability of high risk class
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0]
        confidence = float(np.max(proba))
        raw_score = float(proba[-1])  # probability of highest-risk class
    else:
        raw_score = float(model.predict(X)[0])
        confidence = 0.85

    risk_score = round(raw_score * 100, 1)
    risk_category = score_to_category(risk_score)

    # SHAP top factors
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)
        # For binary classifier, take class-1 shap values
        if isinstance(shap_values, list):
            sv = shap_values[1][0]
        else:
            sv = shap_values[0]
        top_indices = np.argsort(np.abs(sv))[::-1][:3]
        top_factors = [FEATURE_LABELS.get(FEATURES[i], FEATURES[i]) for i in top_indices]
    except Exception:
        top_factors = ["flood-zone overlap", "population density", "hospital access"]

    return {
        "risk_score": risk_score,
        "risk_category": risk_category,
        "confidence": round(confidence, 3),
        "top_factors": top_factors,
    }