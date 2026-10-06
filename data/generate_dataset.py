"""
Credo v2 — Synthetic Business Financial-Wellness Dataset
Reframed from a bank-facing credit tool to a self-serve financial safety tool
for business owners. GST removed. Spending-behavior features added, since
the owner's own logged spending is now a pillar of the score.

5 pillars: UPI/Digital Transaction Health, Banking Stability, EPFO/Payroll
Regularity, Business Stability, Spending Discipline.
"""

import os
import numpy as np
import pandas as pd
from faker import Faker

fake = Faker("en_IN")
np.random.seed(42)

N = 1200
SECTORS = ["Retail Trade", "Manufacturing", "Food & Beverage", "Textiles",
           "Auto Services", "IT/Services", "Construction Materials", "Agri-processing"]

archetypes = np.random.choice(
    ["healthy", "moderate", "at_risk"], size=N, p=[0.40, 0.35, 0.25]
)

rows = []
for i in range(N):
    arche = archetypes[i]
    sector = np.random.choice(SECTORS)
    employees = max(1, int(np.random.gamma(2, 4)))
    years_in_business = round(np.random.uniform(0.5, 15), 1)
    ntc_flag = 1 if years_in_business < 3 or np.random.rand() < 0.3 else 0

    if arche == "healthy":
        upi_txn_consistency = np.random.normal(0.90, 0.06)
        upi_monthly_volume = np.random.normal(450000, 150000)
        inflow_outflow_ratio = np.random.normal(1.25, 0.15)
        bank_balance_avg = np.random.normal(180000, 60000)
        bounce_count_6m = np.random.poisson(0.2)
        epfo_regularity_pct = np.random.normal(94, 4)
        loan_emi_outflow_ratio = np.random.normal(0.18, 0.05)
        spend_logging_consistency = np.random.normal(0.88, 0.08)
        essential_spend_pct = np.random.normal(72, 8)
        monthly_spend_volatility = np.random.normal(0.12, 0.05)
        spend_to_inflow_ratio = np.random.normal(0.55, 0.10)

    elif arche == "moderate":
        upi_txn_consistency = np.random.normal(0.72, 0.08)
        upi_monthly_volume = np.random.normal(220000, 90000)
        inflow_outflow_ratio = np.random.normal(1.05, 0.12)
        bank_balance_avg = np.random.normal(70000, 30000)
        bounce_count_6m = np.random.poisson(1.5)
        epfo_regularity_pct = np.random.normal(75, 8)
        loan_emi_outflow_ratio = np.random.normal(0.32, 0.08)
        spend_logging_consistency = np.random.normal(0.60, 0.12)
        essential_spend_pct = np.random.normal(58, 10)
        monthly_spend_volatility = np.random.normal(0.28, 0.08)
        spend_to_inflow_ratio = np.random.normal(0.75, 0.12)

    else:  # at_risk
        upi_txn_consistency = np.random.normal(0.48, 0.12)
        upi_monthly_volume = np.random.normal(85000, 50000)
        inflow_outflow_ratio = np.random.normal(0.85, 0.15)
        bank_balance_avg = np.random.normal(18000, 12000)
        bounce_count_6m = np.random.poisson(4.5)
        epfo_regularity_pct = np.random.normal(48, 15)
        loan_emi_outflow_ratio = np.random.normal(0.55, 0.12)
        spend_logging_consistency = np.random.normal(0.30, 0.15)
        essential_spend_pct = np.random.normal(40, 12)
        monthly_spend_volatility = np.random.normal(0.48, 0.12)
        spend_to_inflow_ratio = np.random.normal(1.05, 0.18)

    upi_txn_consistency = np.clip(upi_txn_consistency, 0, 1)
    upi_monthly_volume = max(5000, upi_monthly_volume)
    inflow_outflow_ratio = max(0.1, inflow_outflow_ratio)
    bank_balance_avg = max(1000, bank_balance_avg)
    bounce_count_6m = max(0, bounce_count_6m)
    epfo_regularity_pct = np.clip(epfo_regularity_pct, 0, 100)
    loan_emi_outflow_ratio = np.clip(loan_emi_outflow_ratio, 0, 1.2)
    spend_logging_consistency = np.clip(spend_logging_consistency, 0, 1)
    essential_spend_pct = np.clip(essential_spend_pct, 0, 100)
    monthly_spend_volatility = np.clip(monthly_spend_volatility, 0, 1)
    spend_to_inflow_ratio = max(0.05, spend_to_inflow_ratio)

    pillar_upi = upi_txn_consistency * 70 + min(upi_monthly_volume / 10000, 30)
    pillar_banking = min(bank_balance_avg / 3000, 60) + inflow_outflow_ratio * 20 - bounce_count_6m * 5
    pillar_epfo = epfo_regularity_pct
    pillar_stability = years_in_business * 3 + (100 - loan_emi_outflow_ratio * 100) * 0.3
    pillar_spending = (
        spend_logging_consistency * 35 +
        essential_spend_pct * 0.35 +
        (1 - monthly_spend_volatility) * 20 +
        max(0, (1.2 - spend_to_inflow_ratio)) * 10
    )

    pillar_upi = np.clip(pillar_upi, 0, 100)
    pillar_banking = np.clip(pillar_banking, 0, 100)
    pillar_epfo = np.clip(pillar_epfo, 0, 100)
    pillar_stability = np.clip(pillar_stability, 0, 100)
    pillar_spending = np.clip(pillar_spending, 0, 100)

    overall = (
        pillar_upi * 0.25 +
        pillar_banking * 0.25 +
        pillar_epfo * 0.20 +
        pillar_stability * 0.15 +
        pillar_spending * 0.15
    )
    overall = np.clip(overall + np.random.normal(0, 3), 0, 100)

    if overall >= 70:
        safety_band = "Healthy"
    elif overall >= 45:
        safety_band = "Moderate"
    else:
        safety_band = "At-Risk"

    rows.append({
        "business_id": f"BIZ{i+1:05d}",
        "business_name": fake.company(),
        "sector": sector,
        "employees": employees,
        "years_in_business": years_in_business,
        "ntc_flag": ntc_flag,
        "upi_txn_consistency": round(upi_txn_consistency, 3),
        "upi_monthly_volume": round(upi_monthly_volume, 0),
        "inflow_outflow_ratio": round(inflow_outflow_ratio, 2),
        "bank_balance_avg": round(bank_balance_avg, 0),
        "bounce_count_6m": int(bounce_count_6m),
        "epfo_regularity_pct": round(epfo_regularity_pct, 1),
        "loan_emi_outflow_ratio": round(loan_emi_outflow_ratio, 3),
        "spend_logging_consistency": round(spend_logging_consistency, 3),
        "essential_spend_pct": round(essential_spend_pct, 1),
        "monthly_spend_volatility": round(monthly_spend_volatility, 3),
        "spend_to_inflow_ratio": round(spend_to_inflow_ratio, 3),
        "pillar_upi_score": round(pillar_upi, 1),
        "pillar_banking_score": round(pillar_banking, 1),
        "pillar_epfo_score": round(pillar_epfo, 1),
        "pillar_stability_score": round(pillar_stability, 1),
        "pillar_spending_score": round(pillar_spending, 1),
        "financial_health_score": round(overall, 1),
        "safety_band": safety_band,
        "archetype": arche,
    })

df = pd.DataFrame(rows)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "business_financial_wellness_dataset.csv")
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

df.to_csv(OUTPUT_PATH, index=False)
print(f"Generated {len(df)} rows")
print(df["safety_band"].value_counts())
print(df[["financial_health_score"]].describe())
