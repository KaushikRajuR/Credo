"""
Credo Backend API
Serves the trained XGBoost score-prediction model + risk classifier + SHAP
explanations for the frontend dashboard, Shift simulator, and Insight assistant.

Run: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import numpy as np
import pandas as pd

app = FastAPI(title="Credo API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_DIR = "../models"
reg = joblib.load(f"{MODEL_DIR}/score_regressor.pkl")
clf = joblib.load(f"{MODEL_DIR}/risk_classifier.pkl")
le = joblib.load(f"{MODEL_DIR}/risk_label_encoder.pkl")
FEATURES = joblib.load(f"{MODEL_DIR}/feature_list.pkl")
explainer = joblib.load(f"{MODEL_DIR}/shap_explainer.pkl")

FRIENDLY_NAMES = {
    "gst_filing_delay_days": "GST filing delay",
    "gst_compliance_pct": "GST compliance rate",
    "upi_txn_consistency": "UPI transaction consistency",
    "upi_monthly_volume": "UPI monthly volume",
    "inflow_outflow_ratio": "Cash inflow/outflow ratio",
    "bank_balance_avg": "Average bank balance",
    "bounce_count_6m": "Payment bounces (6mo)",
    "epfo_regularity_pct": "EPFO contribution regularity",
    "years_in_business": "Years in business",
    "loan_emi_outflow_ratio": "Existing loan EMI burden",
    "employees": "Employee count",
    "ntc_flag": "New-to-credit status",
}


class MSMEInput(BaseModel):
    gst_filing_delay_days: float = Field(..., ge=0)
    gst_compliance_pct: float = Field(..., ge=0, le=100)
    upi_txn_consistency: float = Field(..., ge=0, le=1)
    upi_monthly_volume: float = Field(..., ge=0)
    inflow_outflow_ratio: float = Field(..., ge=0)
    bank_balance_avg: float = Field(..., ge=0)
    bounce_count_6m: int = Field(..., ge=0)
    epfo_regularity_pct: float = Field(..., ge=0, le=100)
    years_in_business: float = Field(..., ge=0)
    loan_emi_outflow_ratio: float = Field(..., ge=0, le=1.5)
    employees: int = Field(..., ge=1)
    ntc_flag: int = Field(..., ge=0, le=1)


def _predict_core(payload: MSMEInput):
    row = pd.DataFrame([payload.dict()])[FEATURES]
    score = float(np.clip(reg.predict(row)[0], 0, 100))
    band_idx = clf.predict(row)[0]
    band = le.inverse_transform([band_idx])[0]
    shap_values = explainer.shap_values(row)[0]
    return row, score, band, shap_values


@app.post("/api/score/compute")
def compute_score(payload: MSMEInput):
    _, score, band, _ = _predict_core(payload)
    return {"financial_health_score": round(score, 1), "risk_band": band}


@app.post("/api/score/explain")
def explain_score(payload: MSMEInput):
    row, score, band, shap_values = _predict_core(payload)
    contributions = []
    for feat, val in zip(FEATURES, shap_values):
        contributions.append({
            "feature": feat,
            "label": FRIENDLY_NAMES.get(feat, feat),
            "value": round(float(row[feat].iloc[0]), 2),
            "impact": round(float(val), 2),
            "direction": "positive" if val >= 0 else "negative",
        })
    contributions.sort(key=lambda x: abs(x["impact"]), reverse=True)
    return {
        "financial_health_score": round(score, 1),
        "risk_band": band,
        "top_factors": contributions[:5],
        "all_factors": contributions,
    }


@app.post("/api/score/simulate")
def simulate(payload: MSMEInput):
    _, score, band, _ = _predict_core(payload)
    return {"financial_health_score": round(score, 1), "risk_band": band}


class CompareInput(BaseModel):
    past: MSMEInput
    present: MSMEInput


@app.post("/api/score/compare")
def compare(payload: CompareInput):
    _, past_score, past_band, past_shap = _predict_core(payload.past)
    _, present_score, present_band, present_shap = _predict_core(payload.present)

    delta = round(present_score - past_score, 1)
    deltas = []
    for feat, p_val, c_val in zip(FEATURES, past_shap, present_shap):
        deltas.append({
            "feature": feat,
            "label": FRIENDLY_NAMES.get(feat, feat),
            "past_impact": round(float(p_val), 2),
            "present_impact": round(float(c_val), 2),
            "change": round(float(c_val - p_val), 2),
        })
    deltas.sort(key=lambda x: abs(x["change"]), reverse=True)
    top_driver = deltas[0]["label"] if deltas else "overall performance"

    if delta > 0:
        narrative = f"Score improved {delta} pts, driven mainly by {top_driver}."
    elif delta < 0:
        narrative = f"Score fell {abs(delta)} pts, driven mainly by {top_driver}."
    else:
        narrative = "Score remained unchanged."

    return {
        "past_score": round(past_score, 1),
        "past_band": past_band,
        "present_score": round(present_score, 1),
        "present_band": present_band,
        "delta": delta,
        "narrative": narrative,
        "factor_changes": deltas,
    }


@app.get("/api/model/info")
def model_info():
    return {
        "model_type": "XGBoost Regressor + Classifier",
        "training_samples": 1200,
        "regression_mae": 2.79,
        "regression_r2": 0.968,
        "risk_band_accuracy": 0.958,
        "features_used": len(FEATURES),
        "note": "Trained on calibrated synthetic data; production deployment "
                "requires backtesting against real bureau/AA-sourced data."
    }


@app.get("/")
def root():
    return {"status": "Credo API running", "docs": "/docs"}
