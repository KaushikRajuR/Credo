"""
Credo — Financial KPI Engine
Pure-formula financial analysis: no trained model, every number traceable
by hand. This is the core analytical engine behind the Financial Health Score.
"""

def scale_linear(value, low, high, invert=False):
    """Scales a raw KPI value to a 0-100 sub-score.
    If invert=False: higher value -> higher score (low=worst, high=best)
    If invert=True: lower value -> higher score (low=best, high=worst)
    """
    if invert:
        # lower raw value is better (e.g. expense ratio, debt burden)
        if value <= low:
            return 100.0
        if value >= high:
            return 0.0
        return 100.0 * (high - value) / (high - low)
    else:
        # higher raw value is better (e.g. retention rate)
        if value <= low:
            return 0.0
        if value >= high:
            return 100.0
        return 100.0 * (value - low) / (high - low)


def compute_kpis(profile: dict, total_expenses: float, previous_month_expenses: float = None):
    """
    profile keys expected:
      monthly_income, monthly_payroll, monthly_emi_debt, bank_balance,
      previous_month_income, epfo_regularity_pct,
      spend_logging_consistency, essential_spend_pct
    total_expenses: sum of this month's spend_entries (computed from the ledger)
    """
    income = max(profile.get("monthly_income", 0), 0.01)  # avoid div-by-zero
    prev_income = profile.get("previous_month_income", income)
    payroll = profile.get("monthly_payroll", 0)
    emi = profile.get("monthly_emi_debt", 0)

    revenue_growth_pct = ((income - prev_income) / prev_income * 100) if prev_income > 0 else 0.0
    expense_ratio_pct = (total_expenses / income) * 100
    net_cash_flow = income - total_expenses
    cash_retention_pct = (net_cash_flow / income) * 100
    payroll_burden_pct = (payroll / total_expenses * 100) if total_expenses > 0 else 0.0
    debt_burden_pct = (emi / income) * 100

    expense_growth_pct = None
    if previous_month_expenses and previous_month_expenses > 0:
        expense_growth_pct = ((total_expenses - previous_month_expenses) / previous_month_expenses) * 100

    return {
        "revenue_growth_pct": round(revenue_growth_pct, 2),
        "expense_ratio_pct": round(expense_ratio_pct, 2),
        "net_cash_flow": round(net_cash_flow, 2),
        "cash_retention_pct": round(cash_retention_pct, 2),
        "payroll_burden_pct": round(payroll_burden_pct, 2),
        "debt_burden_pct": round(debt_burden_pct, 2),
        "expense_growth_pct": round(expense_growth_pct, 2) if expense_growth_pct is not None else None,
        "total_expenses": round(total_expenses, 2),
        "monthly_income": round(income, 2),
    }


def compute_score(kpis: dict, epfo_regularity_pct: float, spend_logging_consistency: float, essential_spend_pct: float):
    """Converts raw KPIs into weighted 0-100 sub-scores, then the final score."""

    cash_flow_health = scale_linear(kpis["cash_retention_pct"], low=0, high=30, invert=False)
    expense_discipline = scale_linear(kpis["expense_ratio_pct"], low=60, high=100, invert=True)
    debt_safety = scale_linear(kpis["debt_burden_pct"], low=10, high=40, invert=True)
    payroll_stability = scale_linear(epfo_regularity_pct, low=0, high=100, invert=False)
    spending_consistency = scale_linear(
        spend_logging_consistency * 60 + essential_spend_pct * 0.4,
        low=0, high=100, invert=False
    )

    sub_scores = {
        "cash_flow_health": round(cash_flow_health, 1),
        "expense_discipline": round(expense_discipline, 1),
        "debt_safety": round(debt_safety, 1),
        "payroll_stability": round(payroll_stability, 1),
        "spending_consistency": round(spending_consistency, 1),
    }

    WEIGHTS = {
        "cash_flow_health": 0.30,
        "expense_discipline": 0.20,
        "debt_safety": 0.20,
        "payroll_stability": 0.15,
        "spending_consistency": 0.15,
    }

    overall = sum(sub_scores[k] * WEIGHTS[k] for k in WEIGHTS)
    overall = round(overall, 1)

    if overall >= 70:
        band = "Healthy"
    elif overall >= 45:
        band = "Moderate"
    else:
        band = "At-Risk"

    return {
        "financial_health_score": overall,
        "safety_band": band,
        "sub_scores": sub_scores,
        "weights": WEIGHTS,
    }


def detect_anomalies(entries: list, category: str, new_amount: float):
    """Z-score based anomaly check for a new spend entry against its category history."""
    category_amounts = [e["amount"] for e in entries if e["category"] == category]
    if len(category_amounts) < 3:
        return {"is_unusual": False, "reason": "Not enough history in this category to assess yet."}

    mean = sum(category_amounts) / len(category_amounts)
    variance = sum((x - mean) ** 2 for x in category_amounts) / len(category_amounts)
    stdev = variance ** 0.5

    if stdev == 0:
        return {"is_unusual": False, "reason": "No variation in this category's past spending."}

    z_score = (new_amount - mean) / stdev
    is_unusual = z_score > 2

    return {
        "is_unusual": is_unusual,
        "z_score": round(z_score, 2),
        "category_average": round(mean, 2),
        "reason": f"This is {round(z_score, 1)}x standard deviations above your usual {category} spend." if is_unusual else "Within normal range for this category.",
    }
