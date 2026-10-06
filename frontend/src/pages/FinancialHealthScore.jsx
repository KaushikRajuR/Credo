import { useState, useEffect } from "react";
import axios from "axios";
import { Loader2 } from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const sliderFields = [
  { key: "monthly_income", label: "Monthly Income (₹)", min: 0, max: 1000000, step: 5000 },
  { key: "monthly_payroll", label: "Monthly Payroll (₹)", min: 0, max: 300000, step: 5000 },
  { key: "monthly_emi_debt", label: "Monthly EMI/Debt (₹)", min: 0, max: 200000, step: 2000 },
  { key: "epfo_regularity_pct", label: "EPFO Regularity (%)", min: 0, max: 100, step: 1 },
  { key: "spend_logging_consistency", label: "Spend Logging Consistency", min: 0, max: 1, step: 0.01 },
  { key: "essential_spend_pct", label: "Essential Spend Share (%)", min: 0, max: 100, step: 1 },
];

const weightLabels = {
  cash_flow_health: "Cash Flow Health",
  expense_discipline: "Expense Discipline",
  debt_safety: "Debt Safety",
  payroll_stability: "Payroll Stability",
  spending_consistency: "Spending Consistency",
};

export default function FinancialHealthScore() {
  const [profile, setProfile] = useState(null);
  const [result, setResult] = useState(null);
  const [simValues, setSimValues] = useState({});
  const [simResult, setSimResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [simLoading, setSimLoading] = useState(false);

  useEffect(() => {
    const load = async () => {
      const profRes = await axios.get(`${API_URL}/api/profile/get`);
      if (!profRes.data.exists) {
        setLoading(false);
        return;
      }
      setProfile(profRes.data.data);
      setSimValues(profRes.data.data);

      const scoreRes = await axios.get(`${API_URL}/api/score/explain`);
      setResult(scoreRes.data);
      setLoading(false);
    };
    load();
  }, []);

  const runSimulation = async (updatedValues) => {
    setSimLoading(true);
    const payload = {
      monthly_income: Number(updatedValues.monthly_income) || 0,
      previous_month_income: Number(updatedValues.previous_month_income) || 0,
      monthly_payroll: Number(updatedValues.monthly_payroll) || 0,
      monthly_emi_debt: Number(updatedValues.monthly_emi_debt) || 0,
      bank_balance: Number(updatedValues.bank_balance) || 0,
      epfo_regularity_pct: Number(updatedValues.epfo_regularity_pct) || 0,
      spend_logging_consistency: Number(updatedValues.spend_logging_consistency) || 0,
      essential_spend_pct: Number(updatedValues.essential_spend_pct) || 0,
      years_in_business: Number(updatedValues.years_in_business) || 0,
      employees: Number(updatedValues.employees) || 1,
      ntc_flag: Number(updatedValues.ntc_flag) || 0,
    };
    try {
      const res = await axios.post(`${API_URL}/api/score/simulate`, payload);
      setSimResult(res.data);
    } catch (err) {
      console.error(err);
    }
    setSimLoading(false);
  };

  const handleSlider = (key, value) => {
    const updated = { ...simValues, [key]: Number(value) };
    setSimValues(updated);
    runSimulation(updated);
  };

  if (loading) return <div className="px-6 py-8 text-slate-400">Loading...</div>;

  if (!profile) {
    return (
      <div className="px-6 py-8">
        <h2 className="text-2xl font-bold text-slate-800 mb-2">Financial Health Score</h2>
        <p className="text-slate-500">Please fill in My Details first.</p>
      </div>
    );
  }

  const bandColor = {
    Healthy: "text-emerald-600 bg-emerald-50",
    Moderate: "text-amber-600 bg-amber-50",
    "At-Risk": "text-red-600 bg-red-50",
  };

  const displayScore = simResult ? simResult.financial_health_score : result?.financial_health_score;
  const displayBand = simResult ? simResult.safety_band : result?.safety_band;
  const displaySubScores = simResult ? simResult.sub_scores : result?.sub_scores;
  const scoreDelta = simResult ? (simResult.financial_health_score - result.financial_health_score).toFixed(1) : 0;

  return (
    <div className="px-6 py-8 max-w-4xl">
      <h2 className="text-2xl font-bold text-slate-800 mb-1">Financial Health Score</h2>
      <p className="text-slate-500 mb-6">A transparent, weighted score — not a black box.</p>

      {/* Score summary */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-[0_1px_3px_rgba(0,0,0,0.06)] p-6 mb-6 flex items-center justify-between">
        <div>
          <div className="text-4xl font-bold text-slate-800">
            {displayScore}
            {simResult && scoreDelta != 0 && (
              <span className={`text-base ml-2 ${scoreDelta > 0 ? "text-emerald-600" : "text-red-500"}`}>
                ({scoreDelta > 0 ? "+" : ""}{scoreDelta})
              </span>
            )}
          </div>
          <div className={`inline-block mt-2 px-3 py-1 rounded-full text-sm font-semibold ${bandColor[displayBand]}`}>
            {displayBand}
          </div>
        </div>
        {simLoading && <Loader2 className="animate-spin text-slate-300" size={24} />}
      </div>

      {/* Sub-score breakdown with weights */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-[0_1px_3px_rgba(0,0,0,0.06)] p-6 mb-6">
        <h3 className="font-semibold text-slate-700 mb-4">Score Composition</h3>
        <div className="space-y-4">
          {Object.entries(displaySubScores).map(([key, val]) => (
            <div key={key}>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-600">
                  {weightLabels[key]}{" "}
                  <span className="text-slate-400">({(result.weights[key] * 100).toFixed(0)}% weight)</span>
                </span>
                <span className="text-slate-800 font-medium">{val}</span>
              </div>
              <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                <div className="h-full bg-[#1e3a5f]" style={{ width: `${val}%` }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Embedded Shift simulator */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-[0_1px_3px_rgba(0,0,0,0.06)] p-6">
        <h3 className="font-semibold text-slate-700 mb-1">Simulate Changes</h3>
        <p className="text-sm text-slate-400 mb-5">
          Move the sliders to see how changes would affect your score — nothing here is saved.
        </p>
        <div className="space-y-5">
          {sliderFields.map(({ key, label, min, max, step }) => (
            <div key={key}>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-600">{label}</span>
                <span className="text-slate-800 font-medium">{simValues[key]}</span>
              </div>
              <input
                type="range"
                min={min}
                max={max}
                step={step}
                value={simValues[key]}
                onChange={(e) => handleSlider(key, e.target.value)}
                className="w-full accent-[#1e3a5f]"
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
