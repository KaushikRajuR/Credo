import { useState, useEffect } from "react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const kpiMeta = [
  {
    key: "revenue_growth_pct",
    label: "Revenue Growth",
    formula: "(Current Income − Previous Income) / Previous Income × 100",
    unit: "%",
    goodDirection: "higher",
  },
  {
    key: "expense_ratio_pct",
    label: "Expense Ratio",
    formula: "Total Expenses / Monthly Income × 100",
    unit: "%",
    goodDirection: "lower",
  },
  {
    key: "cash_retention_pct",
    label: "Cash Retention Rate",
    formula: "Net Cash Flow / Total Income × 100",
    unit: "%",
    goodDirection: "higher",
  },
  {
    key: "payroll_burden_pct",
    label: "Payroll Burden",
    formula: "Payroll / Total Expenses × 100",
    unit: "%",
    goodDirection: "context",
  },
  {
    key: "debt_burden_pct",
    label: "Debt / EMI Burden",
    formula: "Monthly EMI / Income × 100",
    unit: "%",
    goodDirection: "lower",
  },
  {
    key: "net_cash_flow",
    label: "Net Cash Flow",
    formula: "Monthly Income − Total Expenses",
    unit: "₹",
    goodDirection: "higher",
  },
];

export default function FinancialKPIAnalysis() {
  const [kpis, setKpis] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API_URL}/api/score/explain`).then((res) => {
      if (!res.data.error) setKpis(res.data.kpis);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="px-6 py-8 text-slate-400">Loading...</div>;

  if (!kpis) {
    return (
      <div className="px-6 py-8">
        <h2 className="text-2xl font-bold text-slate-800 mb-2">Financial KPI Analysis</h2>
        <p className="text-slate-500">Please fill in My Details first.</p>
      </div>
    );
  }

  return (
    <div className="px-6 py-8 max-w-4xl">
      <h2 className="text-2xl font-bold text-slate-800 mb-1">Financial KPI Analysis</h2>
      <p className="text-slate-500 mb-6">
        Every number below is calculated directly from your data — no black box.
      </p>

      <div className="grid grid-cols-2 gap-5">
        {kpiMeta.map(({ key, label, formula, unit, goodDirection }) => {
          const value = kpis[key];
          const isGood =
            goodDirection === "higher" ? value >= 0 :
            goodDirection === "lower" ? value <= 30 :
            null;

          return (
            <div
              key={key}
              className="bg-white rounded-xl border border-slate-200 shadow-[0_1px_3px_rgba(0,0,0,0.06)] p-6"
            >
              <div className="text-xs text-slate-400 mb-1">{label}</div>
              <div
                className={`text-3xl font-bold ${
                  isGood === null ? "text-slate-800" : isGood ? "text-emerald-600" : "text-amber-600"
                }`}
              >
                {unit === "₹" ? `₹${value.toLocaleString()}` : `${value}${unit}`}
              </div>
              <div className="text-xs text-slate-400 mt-3 font-mono bg-slate-50 rounded-lg px-3 py-2">
                {formula}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
