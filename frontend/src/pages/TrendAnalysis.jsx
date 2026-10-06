import { useState, useEffect } from "react";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { TrendingUp, TrendingDown, Minus, RefreshCw } from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function TrendAnalysis() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API_URL}/api/score/history`).then((res) => {
      setHistory(res.data.history || []);
      setLoading(false);
    });
  }, []);

  const refreshAndReload = async () => {
    setLoading(true);
    await axios.get(`${API_URL}/api/score/explain`); // triggers a fresh snapshot
    const res = await axios.get(`${API_URL}/api/score/history`);
    setHistory(res.data.history || []);
    setLoading(false);
  };

  if (loading) return <div className="px-6 py-8 text-slate-400">Loading...</div>;

  if (history.length === 0) {
    return (
      <div className="px-6 py-8 max-w-2xl">
        <h2 className="text-2xl font-bold text-slate-800 mb-1">Trend Analysis</h2>
        <p className="text-slate-500 mb-6">Your financial trends over time.</p>
        <div className="bg-white rounded-xl border border-slate-200 shadow-[0_1px_3px_rgba(0,0,0,0.06)] p-10 text-center text-slate-400 text-sm">
          No score history yet — visit Dashboard to compute your first score.
        </div>
      </div>
    );
  }

  const chartData = history.map((h) => ({
    date: new Date(h.computed_at).toLocaleDateString(undefined, { month: "short", day: "numeric" }),
    score: h.financial_health_score,
  }));

  // Past vs Present comparison, now folded into this page
  const oldest = history[0];
  const latest = history[history.length - 1];
  const hasComparison = history.length >= 2;
  const delta = hasComparison ? Math.round((latest.financial_health_score - oldest.financial_health_score) * 10) / 10 : 0;
  const isUp = delta > 0;
  const isFlat = delta === 0;
  const TrendIcon = isFlat ? Minus : isUp ? TrendingUp : TrendingDown;
  const trendColor = isFlat ? "text-slate-400" : isUp ? "text-emerald-600" : "text-red-500";

  const bandColor = {
    Healthy: "text-emerald-600 bg-emerald-50",
    Moderate: "text-amber-600 bg-amber-50",
    "At-Risk": "text-red-600 bg-red-50",
  };

  return (
    <div className="px-6 py-8 max-w-4xl">
      <h2 className="text-2xl font-bold text-slate-800 mb-1">Trend Analysis</h2>
      <button onClick={refreshAndReload} className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-800 mb-4">
        <RefreshCw size={14} /> Refresh now
      </button>
      <p className="text-slate-500 mb-6">How your financial health has moved over time, and where you stand now versus where you started.</p>

      {/* Score over time chart */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-[0_1px_3px_rgba(0,0,0,0.06)] p-6 mb-6">
        <h3 className="font-semibold text-slate-700 mb-4">Score Over Time</h3>
        {history.length < 2 ? (
          <p className="text-sm text-slate-400">Check your score a few more times to build a visible trend.</p>
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="date" tick={{ fontSize: 12, fill: "#94a3b8" }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 12, fill: "#94a3b8" }} />
              <Tooltip />
              <Line type="monotone" dataKey="score" stroke="#334155" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Past vs Present comparison, now part of this page */}
      {hasComparison && (
        <>
          <div className="grid grid-cols-2 gap-5 mb-5">
            <div className="bg-white rounded-xl border border-slate-200 shadow-[0_1px_3px_rgba(0,0,0,0.06)] p-5">
              <div className="text-xs text-slate-400 uppercase tracking-wide">Earliest on Record</div>
              <div className="text-3xl font-bold text-slate-800 mt-1">{oldest.financial_health_score}</div>
              <div className={`inline-block mt-2 px-2.5 py-0.5 rounded-full text-xs font-semibold ${bandColor[oldest.safety_band]}`}>
                {oldest.safety_band}
              </div>
              <div className="text-xs text-slate-400 mt-2">{new Date(oldest.computed_at).toLocaleDateString()}</div>
            </div>
            <div className="bg-white rounded-xl border border-slate-200 shadow-[0_1px_3px_rgba(0,0,0,0.06)] p-5">
              <div className="text-xs text-slate-400 uppercase tracking-wide">Current</div>
              <div className="text-3xl font-bold text-slate-800 mt-1">{latest.financial_health_score}</div>
              <div className={`inline-block mt-2 px-2.5 py-0.5 rounded-full text-xs font-semibold ${bandColor[latest.safety_band]}`}>
                {latest.safety_band}
              </div>
              <div className="text-xs text-slate-400 mt-2">{new Date(latest.computed_at).toLocaleDateString()}</div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 shadow-[0_1px_3px_rgba(0,0,0,0.06)] p-6 flex items-center gap-4">
            <TrendIcon className={trendColor} size={28} />
            <div>
              <div className={`text-base font-semibold ${trendColor}`}>
                {isFlat ? "No change" : `${isUp ? "+" : ""}${delta} points`}
              </div>
              <div className="text-sm text-slate-500">
                {isFlat
                  ? "Your score has stayed steady since your first check."
                  : `Your score has ${isUp ? "improved" : "declined"} by ${Math.abs(delta)} points since your first check.`}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
