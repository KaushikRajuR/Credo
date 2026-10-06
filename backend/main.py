"""
Credo Backend API — Business Financial Wellness (v3, KPI engine based)
Run: uvicorn main:app --reload --port 8000
"""

import os
import json
import io
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic import BaseModel as PydanticBaseModel

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from database import (
    init_db, add_spend_entry, get_spend_entries, get_spend_summary,
    save_score_snapshot, get_latest_and_oldest_snapshot,
    save_profile, get_profile,
    get_current_month_expenses, get_previous_month_expenses,
    get_all_snapshots
)
from kpi_engine import compute_kpis, compute_score, detect_anomalies

load_dotenv()
init_db()

gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

app = FastAPI(title="Credo API", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class BusinessProfile(PydanticBaseModel):
    monthly_income: float = Field(..., ge=0)
    previous_month_income: float = Field(..., ge=0)
    monthly_payroll: float = Field(..., ge=0)
    monthly_emi_debt: float = Field(..., ge=0)
    bank_balance: float = Field(..., ge=0)
    epfo_regularity_pct: float = Field(..., ge=0, le=100)
    spend_logging_consistency: float = Field(..., ge=0, le=1)
    essential_spend_pct: float = Field(..., ge=0, le=100)
    years_in_business: float = Field(..., ge=0)
    employees: int = Field(..., ge=1)
    ntc_flag: int = Field(..., ge=0, le=1)


class SpendEntryInput(PydanticBaseModel):
    amount: float = Field(..., gt=0)
    note: str
    category: str = "Uncategorized"
    is_essential: bool = True


class ChatInput(PydanticBaseModel):
    message: str


SPEND_KEYWORDS = {
    "rent": "Rent", "electricity": "Utilities", "water": "Utilities",
    "salary": "Payroll", "wages": "Payroll", "stock": "Inventory",
    "raw material": "Inventory", "supplies": "Inventory",
    "fuel": "Transport", "transport": "Transport", "delivery": "Transport",
    "marketing": "Marketing", "ads": "Marketing", "advertisement": "Marketing",
    "repair": "Maintenance", "maintenance": "Maintenance",
}


def auto_categorize(note: str) -> str:
    note_lower = note.lower()
    for keyword, category in SPEND_KEYWORDS.items():
        if keyword in note_lower:
            return category
    return "Other"


# ── Score endpoints ───────────────────────────────────────────────────────────

@app.get("/api/score/explain")
def explain_score():
    profile_row = get_profile()
    if not profile_row:
        return {"error": "No profile found. Please fill in My Details first."}
    profile = json.loads(profile_row["data"])

    total_expenses = get_current_month_expenses()
    prev_expenses = get_previous_month_expenses()

    kpis = compute_kpis(profile, total_expenses, prev_expenses)
    score_result = compute_score(
        kpis,
        profile["epfo_regularity_pct"],
        profile["spend_logging_consistency"],
        profile["essential_spend_pct"],
    )

    result = {**score_result, "kpis": kpis}

    pillar_data = json.dumps(score_result["sub_scores"])
    save_score_snapshot(score_result["financial_health_score"], score_result["safety_band"], pillar_data)

    return result


@app.post("/api/score/simulate")
def simulate_score(payload: BusinessProfile):
    """Powers the Shift panel — uses hypothetical profile values, real current-month expenses."""
    total_expenses = get_current_month_expenses()
    prev_expenses = get_previous_month_expenses()
    profile = payload.dict()

    kpis = compute_kpis(profile, total_expenses, prev_expenses)
    score_result = compute_score(
        kpis,
        profile["epfo_regularity_pct"],
        profile["spend_logging_consistency"],
        profile["essential_spend_pct"],
    )
    return {**score_result, "kpis": kpis}


@app.get("/api/score/compare")
def compare_snapshots():
    latest, oldest = get_latest_and_oldest_snapshot()
    if not latest or not oldest or latest["id"] == oldest["id"]:
        return {"available": False, "message": "Not enough history yet — check back after your next score update."}

    delta = round(latest["financial_health_score"] - oldest["financial_health_score"], 1)
    if delta > 0:
        narrative = f"Your score improved {delta} pts over the past period."
    elif delta < 0:
        narrative = f"Your score dropped {abs(delta)} pts over the past period."
    else:
        narrative = "Your score has stayed steady."

    return {
        "available": True,
        "past_score": oldest["financial_health_score"],
        "past_band": oldest["safety_band"],
        "past_date": oldest["computed_at"],
        "present_score": latest["financial_health_score"],
        "present_band": latest["safety_band"],
        "present_date": latest["computed_at"],
        "delta": delta,
        "narrative": narrative,
    }


@app.get("/api/score/history")
def score_history():
    snapshots = get_all_snapshots()
    return {"history": snapshots}



# ── Spending endpoints ────────────────────────────────────────────────────────

@app.post("/api/spending/log")
def log_spend(entry: SpendEntryInput):
    category = entry.category if entry.category != "Uncategorized" else auto_categorize(entry.note)
    existing_entries = get_spend_entries(limit=200)
    anomaly = detect_anomalies(existing_entries, category, entry.amount)
    add_spend_entry(entry.amount, entry.note, category, entry.is_essential)
    return {"status": "saved", "category": category, "anomaly": anomaly}


@app.get("/api/spending/list")
def list_spend(limit: int = 50):
    return {"entries": get_spend_entries(limit)}


@app.get("/api/spending/summary")
def spend_summary():
    return get_spend_summary()


@app.post("/api/spending/categorize")
def categorize_preview(note: str):
    return {"suggested_category": auto_categorize(note)}


# ── Profile endpoints ─────────────────────────────────────────────────────────

@app.post("/api/profile/save")
def save_business_profile(payload: BusinessProfile):
    save_profile(json.dumps(payload.dict()))
    return {"status": "saved"}


@app.get("/api/profile/get")
def get_business_profile():
    profile = get_profile()
    if not profile:
        return {"exists": False}
    return {"exists": True, "data": json.loads(profile["data"]), "updated_at": profile["updated_at"]}


import time

def call_gemini_with_retry(prompt, retries=2):
    for attempt in range(retries):
        try:
            response = gemini_client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
            )
            return response.text
        except Exception as e:
            if "503" in str(e) and attempt < retries - 1:
                time.sleep(2)
                continue
            raise e


# ── Insight endpoint ──────────────────────────────────────────────────────────

@app.post("/api/insight/chat")
def insight_chat(payload: ChatInput):
    profile_row = get_profile()
    context = "No profile data available yet — the user hasn't filled in My Details."

    if profile_row:
        profile = json.loads(profile_row["data"])
        total_expenses = get_current_month_expenses()
        prev_expenses = get_previous_month_expenses()

        kpis = compute_kpis(profile, total_expenses, prev_expenses)
        score_result = compute_score(
            kpis,
            profile["epfo_regularity_pct"],
            profile["spend_logging_consistency"],
            profile["essential_spend_pct"],
        )

        history = get_all_snapshots(limit=2)
        trend_note = ""
        if len(history) >= 2:
            prev_score = history[-2]["financial_health_score"]
            curr_score = history[-1]["financial_health_score"]
            delta = round(curr_score - prev_score, 1)
            trend_note = f" The score moved from {prev_score} to {curr_score} ({'+' if delta >= 0 else ''}{delta} pts) since the last check."

        context = (
            f"Current Financial Health Score: {score_result['financial_health_score']} ({score_result['safety_band']}).{trend_note}\n"
            f"Score breakdown (0-100 each, weighted): {json.dumps(score_result['sub_scores'])}\n"
            f"Key financial KPIs this month:\n"
            f"- Monthly Income: Rs.{kpis['monthly_income']}\n"
            f"- Total Expenses: Rs.{kpis['total_expenses']}\n"
            f"- Net Cash Flow: Rs.{kpis['net_cash_flow']}\n"
            f"- Expense Ratio: {kpis['expense_ratio_pct']}%\n"
            f"- Cash Retention Rate: {kpis['cash_retention_pct']}%\n"
            f"- Revenue Growth: {kpis['revenue_growth_pct']}%\n"
            f"- Payroll Burden: {kpis['payroll_burden_pct']}%\n"
            f"- Debt/EMI Burden: {kpis['debt_burden_pct']}%\n"
        )
        if kpis.get("expense_growth_pct") is not None:
            context += f"- Expense Growth vs last month: {kpis['expense_growth_pct']}%\n"

    system_prompt = (
        "You are Insight, a financial wellness assistant inside the Credo app for small business owners. "
        "Your job is to explain the user's REAL computed financial KPIs and score breakdown in plain language — "
        "you are not making predictions or guesses, you are interpreting actual numbers already calculated for them. "
        "When asked why the score changed, point to the specific KPI(s) that moved and explain the relationship "
        "(e.g. 'your score dropped mainly because your Expense Ratio rose, meaning expenses grew faster than income'). "
        "Be concise, plain-language, and encouraging but honest. Never give formal financial/legal advice — "
        "frame things as observations and suggestions based on their own data.\n\n"
        f"Here is the user's current data:\n{context}"
    )

    try:
        reply = call_gemini_with_retry(f"{system_prompt}\n\nUser question: {payload.message}")
    except Exception as e:
        reply = "Sorry, I couldn't process that right now. Please try again."
        print(f"Gemini error: {e}")

    return {"reply": reply}



# ── Export endpoint ───────────────────────────────────────────────────────────

@app.get("/api/export/pdf")
def export_pdf():
    profile_row = get_profile()
    if not profile_row:
        return {"error": "No profile data found. Please fill in My Details first."}

    profile = json.loads(profile_row["data"])
    total_expenses = get_current_month_expenses()
    prev_expenses = get_previous_month_expenses()

    kpis = compute_kpis(profile, total_expenses, prev_expenses)
    score_result = compute_score(
        kpis,
        profile["epfo_regularity_pct"],
        profile["spend_logging_consistency"],
        profile["essential_spend_pct"],
    )

    spend_summary = get_spend_summary()
    spend_entries = get_spend_entries(limit=50)

    score = score_result["financial_health_score"]
    band = score_result["safety_band"]

    band_colors = {
        "Healthy": colors.HexColor("#059669"),
        "Moderate": colors.HexColor("#d97706"),
        "At-Risk": colors.HexColor("#dc2626"),
    }
    band_color = band_colors.get(band, colors.HexColor("#334155"))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"], fontSize=20, spaceAfter=2)
    subtitle_style = ParagraphStyle("SubtitleStyle", parent=styles["Normal"], textColor=colors.HexColor("#64748b"), fontSize=10, spaceAfter=16)
    score_style = ParagraphStyle("ScoreStyle", parent=styles["Normal"], fontSize=36, textColor=colors.HexColor("#1e293b"), spaceAfter=2)
    band_style = ParagraphStyle("BandStyle", parent=styles["Normal"], fontSize=12, textColor=band_color, spaceAfter=16)
    section_style = ParagraphStyle("SectionStyle", parent=styles["Heading2"], fontSize=13, spaceBefore=16, spaceAfter=6)
    disclaimer_style = ParagraphStyle("DisclaimerStyle", parent=styles["Normal"], fontSize=8, textColor=colors.HexColor("#94a3b8"), spaceBefore=20)

    elements = []
    elements.append(Paragraph("Credo — Financial Health Card", title_style))
    elements.append(Paragraph(f"Generated on {datetime.utcnow().strftime('%d %b %Y')}", subtitle_style))

    elements.append(Paragraph(str(score), score_style))
    elements.append(Paragraph(band, band_style))

    # ---- NEW: Financial KPI section ----
    elements.append(Paragraph("Financial KPIs", section_style))
    kpi_data = [
        ["Metric", "Value"],
        ["Monthly Income", f"Rs. {kpis['monthly_income']:,.0f}"],
        ["Total Expenses", f"Rs. {kpis['total_expenses']:,.0f}"],
        ["Net Cash Flow", f"Rs. {kpis['net_cash_flow']:,.0f}"],
        ["Revenue Growth", f"{kpis['revenue_growth_pct']}%"],
        ["Expense Ratio", f"{kpis['expense_ratio_pct']}%"],
        ["Cash Retention Rate", f"{kpis['cash_retention_pct']}%"],
        ["Payroll Burden", f"{kpis['payroll_burden_pct']}%"],
        ["Debt/EMI Burden", f"{kpis['debt_burden_pct']}%"],
    ]
    kpi_table = Table(kpi_data, colWidths=[80*mm, 60*mm])
    kpi_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#64748b")),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#e2e8f0")),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, colors.HexColor("#f1f5f9")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(kpi_table)

    # ---- NEW: Score breakdown section ----
    elements.append(Paragraph("Score Composition", section_style))
    sub_score_data = [["Component", "Weight", "Score"]]
    for key, val in score_result["sub_scores"].items():
        weight_pct = f"{score_result['weights'][key] * 100:.0f}%"
        sub_score_data.append([key.replace("_", " ").title(), weight_pct, str(val)])
    sub_score_table = Table(sub_score_data, colWidths=[70*mm, 35*mm, 35*mm])
    sub_score_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#64748b")),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#e2e8f0")),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, colors.HexColor("#f1f5f9")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(sub_score_table)

    # Spending summary (existing)
    elements.append(Paragraph("Monthly Spending Summary", section_style))
    summary_data = [
        ["Total Spent", "Essential", "Discretionary"],
        [f"Rs. {spend_summary['total_spent']:,.0f}",
         f"Rs. {spend_summary['essential_spent']:,.0f}",
         f"Rs. {spend_summary['discretionary_spent']:,.0f}"],
    ]
    summary_table = Table(summary_data, colWidths=[55*mm]*3)
    summary_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#64748b")),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(summary_table)

    elements.append(Paragraph("Spending Entries", section_style))
    if spend_entries:
        table_data = [["Date", "Note", "Category", "Amount"]]
        for e in spend_entries:
            table_data.append([
                e["logged_at"][:10],
                e["note"][:35],
                e["category"],
                f"Rs. {e['amount']:,.0f}",
            ])
        entries_table = Table(table_data, colWidths=[25*mm, 70*mm, 35*mm, 30*mm])
        entries_table.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#64748b")),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#e2e8f0")),
            ("LINEBELOW", (0, 1), (-1, -1), 0.3, colors.HexColor("#f1f5f9")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("ALIGN", (3, 0), (3, -1), "RIGHT"),
        ]))
        elements.append(entries_table)
    else:
        elements.append(Paragraph("No spending entries logged yet.", styles["Normal"]))

    elements.append(Paragraph(
        "This card is calculated from transparent, documented financial formulas applied to the "
        "business owner's self-reported profile and logged spending data — not a predictive model. "
        "Intended for personal financial awareness, not as a formal credit assessment.",
        disclaimer_style
    ))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return Response(content=pdf_bytes, media_type="application/pdf",
                     headers={"Content-Disposition": "attachment; filename=credo_financial_health_card.pdf"})



# ── Meta endpoints ────────────────────────────────────────────────────────────

@app.get("/api/model/info")
def model_info():
    return {
        "model_type": "Deterministic KPI Engine",
        "features_used": 11,
        "note": "Pure-formula financial analysis engine converting business KPIs to sub-scores."
    }


@app.get("/")
def root():
    return {"status": "Credo API running", "docs": "/docs"}
