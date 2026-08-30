import { useState } from "react";
import axios from "axios";
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer } from "recharts";

const API_URL = import.meta.env.VITE_API_URL;

// Sample input — replace with real form data later (My Details page)
const sampleInput = {
  gst_filing_delay_days: 3,
  gst_compliance_pct: 94,
  upi_txn_consistency: 0.88,
  upi_monthly_volume: 380000,
  inflow_outflow_ratio: 1.2,
  bank_balance_avg: 150000,
  bounce_count_6m: 0,
  epfo_regularity_pct: 90,
  years_in_business: 5,
  loan_emi_outflow_ratio: 0.2,
  employees: 8,
  ntc_flag: 0,
};

export default function Dashboard() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchScore = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/api/score/explain`, sampleInput);
      setResult(res.data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const bandColor = {
    Healthy: "text-emerald-600 bg-emerald-50",
    Moderate: "text-amber-600 bg-amber-50",
    "High-Risk": "text-red-600 bg-red-50",
  };

  const radarData = result
    ? [
        { pillar: "GST", value: 100 - Math.abs(result.top_factors.find(f => f.feature.includes("gst_compliance"))?.value || 0) },
      ]
    : [];

  return (
    <div className="p-8 max-w-5xl">
      <h2 className="text-2xl font-bold text-slate-800 mb-1">Dashboard</h2>
      <p className="text-slate-500 mb-6">Your business's live financial health snapshot</p>

      {!result && (
        <button
          onClick={fetchScore}
          disabled={loading}
          className="px-5 py-2.5 bg-teal-600 text-white rounded-lg font-medium hover:bg-teal-700 transition-colors disabled:opacity-50"
        >
          {loading ? "Computing..." : "Compute My Score"}
        </button>
      )}

      {result && (
        <div className="grid grid-cols-2 gap-6 mt-4">
          <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-8 flex flex-col items-center justify-center">
            <div className="text-6xl font-bold text-slate-800">{result.financial_health_score}</div>
            <div className={`mt-3 px-4 py-1 rounded-full text-sm font-semibold ${bandColor[result.risk_band]}`}>
              {result.risk_band}
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
            <h3 className="font-semibold text-slate-700 mb-4">Top Factors</h3>
            <div className="space-y-3">
              {result.top_factors.map((f) => (
                <div key={f.feature} className="flex justify-between items-center text-sm">
                  <span className="text-slate-600">{f.label}</span>
                  <span className={`font-semibold ${f.direction === "positive" ? "text-emerald-600" : "text-red-500"}`}>
                    {f.direction === "positive" ? "+" : ""}{f.impact}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}