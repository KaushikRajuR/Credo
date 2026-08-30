"""
Credo — Model Training
Trains an XGBoost regressor to predict the MSME Financial Health Score (0-100)
from raw alt-data signals, plus a classifier for risk band, with SHAP explainability.
"""

import pandas as pd
import numpy as np
import joblib
import shap
from xgboost import XGBRegressor, XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

df = pd.read_csv("../data/msme_synthetic_dataset.csv")

FEATURES = [
    "gst_filing_delay_days", "gst_compliance_pct",
    "upi_txn_consistency", "upi_monthly_volume", "inflow_outflow_ratio",
    "bank_balance_avg", "bounce_count_6m",
    "epfo_regularity_pct",
    "years_in_business", "loan_emi_outflow_ratio", "employees", "ntc_flag",
]

X = df[FEATURES]
y_score = df["financial_health_score"]
y_band = df["risk_band"]

le = LabelEncoder()
y_band_enc = le.fit_transform(y_band)

X_train, X_test, y_train, y_test, yb_train, yb_test = train_test_split(
    X, y_score, y_band_enc, test_size=0.2, random_state=42
)

# ---- Regression model ----
reg = XGBRegressor(
    n_estimators=250, max_depth=4, learning_rate=0.06,
    subsample=0.85, colsample_bytree=0.85, random_state=42
)
reg.fit(X_train, y_train)
pred = reg.predict(X_test)

mae = mean_absolute_error(y_test, pred)
r2 = r2_score(y_test, pred)
print(f"Regression — MAE: {mae:.2f} points | R2: {r2:.3f}")

# ---- Classification model ----
clf = XGBClassifier(
    n_estimators=200, max_depth=4, learning_rate=0.08,
    subsample=0.85, colsample_bytree=0.85, random_state=42,
    eval_metric="mlogloss"
)
clf.fit(X_train, yb_train)
band_pred = clf.predict(X_test)
acc = accuracy_score(yb_test, band_pred)
print(f"Classification — Risk Band Accuracy: {acc:.3f}")
print(classification_report(yb_test, band_pred, target_names=le.classes_))

# ---- SHAP explainer ----
explainer = shap.TreeExplainer(reg)

# Save all artifacts
joblib.dump(reg, "../models/score_regressor.pkl")
joblib.dump(clf, "../models/risk_classifier.pkl")
joblib.dump(le, "../models/risk_label_encoder.pkl")
joblib.dump(FEATURES, "../models/feature_list.pkl")
joblib.dump(explainer, "../models/shap_explainer.pkl")

importance = pd.Series(reg.feature_importances_, index=FEATURES).sort_values(ascending=False)
print("\nTop feature importances:")
print(importance)
importance.to_csv("../models/feature_importance.csv")

print("\nModels saved to ../models/")
