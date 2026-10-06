"""
Credo — Local SQLite storage for spend entries and score snapshots.
Lightweight, file-based — no external DB setup needed for the hackathon build.
"""

import sqlite3
from datetime import datetime, timedelta
from contextlib import contextmanager

DB_PATH = "credo.db"


def init_profile_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS business_profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            data TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS spend_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                note TEXT NOT NULL,
                category TEXT,
                is_essential INTEGER,
                logged_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS score_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                financial_health_score REAL NOT NULL,
                safety_band TEXT NOT NULL,
                pillar_data TEXT,
                computed_at TEXT NOT NULL
            )
        """)
        init_profile_table(conn)
        conn.commit()


def save_profile(data_json):
    with get_conn() as conn:
        init_profile_table(conn)
        conn.execute(
            "INSERT INTO business_profile (id, data, updated_at) VALUES (1, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET data = excluded.data, updated_at = excluded.updated_at",
            (data_json, datetime.utcnow().isoformat())
        )
        conn.commit()


def get_profile():
    with get_conn() as conn:
        init_profile_table(conn)
        row = conn.execute("SELECT * FROM business_profile WHERE id = 1").fetchone()
        return dict(row) if row else None



@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def add_spend_entry(amount, note, category, is_essential):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO spend_entries (amount, note, category, is_essential, logged_at) VALUES (?, ?, ?, ?, ?)",
            (amount, note, category, int(is_essential), datetime.utcnow().isoformat())
        )
        conn.commit()


def get_spend_entries(limit=100):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM spend_entries ORDER BY logged_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_spend_summary():
    with get_conn() as conn:
        rows = conn.execute("SELECT amount, is_essential, category FROM spend_entries").fetchall()
        total = sum(r["amount"] for r in rows)
        essential = sum(r["amount"] for r in rows if r["is_essential"])
        discretionary = total - essential
        by_category = {}
        for r in rows:
            cat = r["category"] or "Uncategorized"
            by_category[cat] = by_category.get(cat, 0) + r["amount"]
        return {
            "total_spent": round(total, 2),
            "essential_spent": round(essential, 2),
            "discretionary_spent": round(discretionary, 2),
            "entry_count": len(rows),
            "by_category": by_category,
        }


def save_score_snapshot(score, band, pillar_data_json):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO score_snapshots (financial_health_score, safety_band, pillar_data, computed_at) VALUES (?, ?, ?, ?)",
            (score, band, pillar_data_json, datetime.utcnow().isoformat())
        )
        conn.commit()
        # prune anything older than 1 month — only recent history is kept
        cutoff = (datetime.utcnow() - timedelta(days=30)).isoformat()
        conn.execute("DELETE FROM score_snapshots WHERE computed_at < ?", (cutoff,))
        conn.commit()


def get_latest_and_oldest_snapshot():
    with get_conn() as conn:
        latest = conn.execute(
            "SELECT * FROM score_snapshots ORDER BY computed_at DESC LIMIT 1"
        ).fetchone()
        oldest = conn.execute(
            "SELECT * FROM score_snapshots ORDER BY computed_at ASC LIMIT 1"
        ).fetchone()
        return (dict(latest) if latest else None, dict(oldest) if oldest else None)


def get_current_month_expenses():
    now = datetime.utcnow()
    month_prefix = now.strftime("%Y-%m")
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT amount FROM spend_entries WHERE logged_at LIKE ?",
            (f"{month_prefix}%",)
        ).fetchall()
        return sum(r["amount"] for r in rows)


def get_previous_month_expenses():
    now = datetime.utcnow()
    prev_month = (now.month - 1) or 12
    prev_year = now.year if now.month > 1 else now.year - 1
    month_prefix = f"{prev_year}-{prev_month:02d}"
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT amount FROM spend_entries WHERE logged_at LIKE ?",
            (f"{month_prefix}%",)
        ).fetchall()
        return sum(r["amount"] for r in rows)


def get_all_snapshots(limit=60):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM score_snapshots ORDER BY computed_at ASC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


