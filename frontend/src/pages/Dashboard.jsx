import { useState, useEffect } from "react";
import axios from "axios";
import { Loader2 } from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function Dashboard() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [noProfile, setNoProfile] = useState(false);

  const fetchScore = async () => {
    setLoading(true);
    setNoProfile(false);
    try {
      const res = await axios.get(`${API_URL}/api/score/explain`);
      if (res.data.error) {
        setNoProfile(true);
      } else {
        setResult(res.data);
      }
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchScore();
  }, []);

  const bandColor = {
    Healthy: "text-emerald-600 bg-emerald-50",
    Moderate: "text-amber-600 bg-amber-50",
    "At-Risk": "text-red-600 bg-red-50",
  };

  if (loading) {
    return <div className="px-6 py-8 text-slate-400">Loading...</div>;
  }

  if (noProfile) {
    return (
      <div className="px-6 py-8 max-w-2xl">
        <h2 className="text-2xl font-bold text-slate-800 mb-1">Dashboard</h2>
        <div className="bg-white rounded-xl border border-slate-200 shadow-[0_1px_3px_rgba(0,0,0,0.06)] p-10 text-center mt-4">
          <p className="text-slate-500">Please fill in My Details first to see your dashboard.</p>
        </div>
      </div>
    );
  }

  if (!result) return null;

  const { financial_health_score, safety_band, kpis, sub_scores } = result;

  return (
    <div className="px-6 py-8 max-w-5xl">
      <h2 className="text-2xl font-bold text-slate-800 mb-1">Dashboard</h2>
      <p className="text-slate-500 mb-6">Your business's live financial snapshot.</p>

      <div className="grid grid-cols-3 gap-5 mb-6">
        {/* Score card */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-[0_1px_3px_rgba(0,0,0,0.06)] p-6 flex flex-col items-center justify-center text-center">
          <div className="text-5xl font-bold text-slate-800">{financial_health_score}</div>
          <div className={`mt-2 px-3 py-1 rounded-full text-sm font-semibold ${bandColor[safety_band]}`}>
            {safety_band}
          </div>
        </div>

        {/* Cash flow */}
        <KPITile
          label="Net Cash Flow"
          value={`₹${kpis.net_cash_flow.toLocaleString()}`}
          sub={`${kpis.cash_retention_pct}% of income retained`}
          positive={kpis.net_cash_flow >= 0}
        />

        {/* Revenue growth */}
        <KPITile
          label="Revenue Growth"
          value={`${kpis.revenue_growth_pct >= 0 ? "+" : ""}${kpis.revenue_growth_pct}%`}
          sub="vs. last month"
          positive={kpis.revenue_growth_pct >= 0}
        />
      </div>

      <div className="grid grid-cols-2 gap-5">
        {/* Raw numbers */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-[0_1px_3px_rgba(0,0,0,0.06)] p-6">
          <h3 className="font-semibold text-slate-700 mb-4">This Month</h3>
          <div className="space-y-2.5 text-sm">
            <Row label="Income" value={`₹${kpis.monthly_income.toLocaleString()}`} />
            <Row label="Expenses" value={`₹${kpis.total_expenses.toLocaleString()}`} />
            <Row label="Expense Ratio" value={`${kpis.expense_ratio_pct}%`} />
            <Row label="Payroll Burden" value={`${kpis.payroll_burden_pct}%`} />
            <Row label="Debt/EMI Burden" value={`${kpis.debt_burden_pct}%`} />
          </div>
        </div>

        {/* Sub-scores */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-[0_1px_3px_rgba(0,0,0,0.06)] p-6">
          <h3 className="font-semibold text-slate-700 mb-4">Score Breakdown</h3>
          <div className="space-y-3">
            {Object.entries(sub_scores).map(([key, val]) => (
              <div key={key}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-600 capitalize">{key.replace(/_/g, " ")}</span>
                  <span className="text-slate-800 font-medium">{val}</span>
                </div>
                <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-[#1e3a5f]" style={{ width: `${val}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function KPITile({ label, value, sub, positive }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-[0_1px_3px_rgba(0,0,0,0.06)] p-6">
      <div className="text-xs text-slate-400 mb-1">{label}</div>
      <div className={`text-2xl font-bold ${positive ? "text-emerald-600" : "text-red-500"}`}>{value}</div>
      <div className="text-xs text-slate-400 mt-1">{sub}</div>
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div className="flex justify-between">
      <span className="text-slate-500">{label}</span>
      <span className="text-slate-800 font-medium">{value}</span>
    </div>
  );
}