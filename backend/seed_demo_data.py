"""
One-time seed script: backdates realistic score snapshots and spending
entries across September so Trend Analysis and My Spending have a full
month of demo history. Run this manually once:  python seed_demo_data.py
"""

import sqlite3
import json
import random
from datetime import datetime, timedelta

DB_PATH = "credo.db"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

# ---- Clear any existing demo-range data first (avoid duplicates on re-run) ----
conn.execute("DELETE FROM score_snapshots WHERE computed_at < '2026-10-01'")
conn.execute("DELETE FROM spend_entries WHERE logged_at < '2026-10-01'")
conn.commit()

# ============ SCORE SNAPSHOTS: Sept 1 - Sept 30 ============
# Gentle upward trend with realistic day-to-day noise
start_score = 58.0
end_score = 74.0
days = 30
start_date = datetime(2026, 9, 1, 10, 0, 0)

bands = lambda s: "Healthy" if s >= 70 else ("Moderate" if s >= 45 else "At-Risk")

score_rows = []
for i in range(days):
    # not every day has a check-in — roughly every 1-3 days, realistic usage pattern
    if random.random() < 0.6:
        progress = i / (days - 1)
        base_score = start_score + (end_score - start_score) * progress
        noise = random.uniform(-2.5, 2.5)
        score = round(max(0, min(100, base_score + noise)), 1)
        band = bands(score)
        date = start_date + timedelta(days=i, hours=random.randint(0, 10))
        sub_scores = {
            "cash_flow_health": round(score * random.uniform(0.9, 1.05), 1),
            "expense_discipline": round(score * random.uniform(0.85, 1.1), 1),
            "debt_safety": round(score * random.uniform(0.9, 1.05), 1),
            "payroll_stability": round(score * random.uniform(0.95, 1.05), 1),
            "spending_consistency": round(score * random.uniform(0.85, 1.1), 1),
        }
        score_rows.append((score, band, json.dumps(sub_scores), date.isoformat()))

conn.executemany(
    "INSERT INTO score_snapshots (financial_health_score, safety_band, pillar_data, computed_at) VALUES (?, ?, ?, ?)",
    score_rows
)
conn.commit()
print(f"Inserted {len(score_rows)} score snapshots across September.")

# ============ SPENDING ENTRIES: Sept 1 - Sept 30 ============
# Edit this list freely — add/remove/change entries as you like before running
spend_entries = [
    (4500, "Shop rent payment", "Rent", True),
    (1200, "Electricity bill", "Utilities", True),
    (8000, "Raw material restock", "Inventory", True),
    (650, "Fuel for delivery van", "Transport", True),
    (300, "Tea and snacks for staff", "Other", False),
    (15000, "Staff salary advance", "Payroll", True),
    (2200, "Instagram ads boost", "Marketing", False),
    (900, "Packaging supplies", "Inventory", True),
    (500, "Printer ink cartridge", "Other", False),
    (3200, "Equipment repair", "Maintenance", True),
    (1100, "Water bill", "Utilities", True),
    (6500, "New stock purchase", "Inventory", True),
    (450, "Courier charges", "Transport", True),
    (1800, "Diwali decoration for shop", "Other", False),
    (12000, "Monthly staff salary", "Payroll", True),
    (700, "Internet bill", "Utilities", True),
    (2500, "Local newspaper ad", "Marketing", False),
    (950, "Stationery and billing books", "Other", True),
    (4200, "Generator fuel", "Utilities", True),
    (5000, "EMI payment - equipment loan", "Other", True),
    (300, "Tea for client meeting", "Other", False),
    (2800, "Replacement parts", "Maintenance", True),
    (7500, "Bulk inventory purchase", "Inventory", True),
    (600, "Mobile recharge for business line", "Utilities", True),
    (1500, "Flyers printing", "Marketing", False),
]

random.shuffle(spend_entries)
spend_rows = []
for i, (amount, note, category, is_essential) in enumerate(spend_entries):
    day_offset = random.randint(0, 29)
    date = datetime(2026, 9, 1) + timedelta(days=day_offset, hours=random.randint(8, 20))
    spend_rows.append((amount, note, category, int(is_essential), date.isoformat()))

spend_rows.sort(key=lambda r: r[4])

conn.executemany(
    "INSERT INTO spend_entries (amount, note, category, is_essential, logged_at) VALUES (?, ?, ?, ?, ?)",
    spend_rows
)
conn.commit()
print(f"Inserted {len(spend_rows)} spending entries across September.")

conn.close()
print("Seed complete.")
