import { useState, useEffect } from "react";
import axios from "axios";
import { Loader2, Check } from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const emptyProfile = {
  monthly_income: "",
  previous_month_income: "",
  monthly_payroll: "",
  monthly_emi_debt: "",
  bank_balance: "",
  epfo_regularity_pct: "",
  spend_logging_consistency: "",
  essential_spend_pct: "",
  years_in_business: "",
  employees: "",
  ntc_flag: 0,
};

const fieldGroups = [
  {
    title: "Income & Cash",
    fields: [
      { key: "monthly_income", label: "This Month's Income (₹)" },
      { key: "previous_month_income", label: "Last Month's Income (₹)" },
      { key: "bank_balance", label: "Current Bank Balance (₹)" },
    ],
  },
  {
    title: "Fixed Obligations",
    fields: [
      { key: "monthly_payroll", label: "Monthly Payroll (₹)" },
      { key: "monthly_emi_debt", label: "Monthly EMI / Debt Payments (₹)" },
      { key: "epfo_regularity_pct", label: "EPFO Contribution Regularity (%)" },
    ],
  },
  {
    title: "Spending Behaviour",
    fields: [
      { key: "spend_logging_consistency", label: "How Consistently You Log Spend (0-1)" },
      { key: "essential_spend_pct", label: "Essential Spend Share (%)" },
    ],
  },
  {
    title: "Business Context",
    fields: [
      { key: "years_in_business", label: "Years in Business" },
      { key: "employees", label: "Number of Employees" },
    ],
  },
];

export default function MyDetails() {
  const [form, setForm] = useState(emptyProfile);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    axios.get(`${API_URL}/api/profile/get`).then((res) => {
      if (res.data.exists) setForm({ ...emptyProfile, ...res.data.data });
    });
  }, []);

  const update = (key, value) => {
    setForm((f) => ({ ...f, [key]: value }));
    setSaved(false);
  };

  const handleSave = async () => {
    setSaving(true);
    const payload = {};
    Object.keys(emptyProfile).forEach((k) => {
      payload[k] = k === "ntc_flag" ? form[k] : Number(form[k]);
    });
    try {
      await axios.post(`${API_URL}/api/profile/save`, payload);
      setSaved(true);
    } catch (err) {
      console.error(err);
    }
    setSaving(false);
  };

  return (
    <div className="px-6 py-8 max-w-2xl">
      <h2 className="text-2xl font-bold text-slate-800 mb-1">My Details</h2>
      <p className="text-slate-500 mb-6">
        This data powers your Financial Health Score and KPIs — update it anytime.
        Your monthly expenses are calculated automatically from My Spending.
      </p>

      <div className="bg-white rounded-xl shadow-[0_1px_3px_rgba(0,0,0,0.06)] border border-slate-200 p-6 space-y-6">
        {fieldGroups.map((group) => (
          <div key={group.title}>
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-3">
              {group.title}
            </h3>
            <div className="grid grid-cols-2 gap-4">
              {group.fields.map(({ key, label }) => (
                <div key={key}>
                  <label className="block text-xs text-slate-500 mb-1">{label}</label>
                  <input
                    type="number"
                    step="0.01"
                    value={form[key]}
                    onChange={(e) => update(key, e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-slate-400"
                  />
                </div>
              ))}
            </div>
          </div>
        ))}

        <label className="flex items-center gap-2 text-sm text-slate-500">
          <input
            type="checkbox"
            checked={!!form.ntc_flag}
            onChange={(e) => update("ntc_flag", e.target.checked ? 1 : 0)}
          />
          New-to-credit business
        </label>

        <button
          onClick={handleSave}
          disabled={saving}
          className="px-5 py-2.5 bg-[#1e3a5f] text-white rounded-lg text-sm font-medium hover:bg-[#16293f] disabled:opacity-50 flex items-center gap-2"
        >
          {saving ? <Loader2 size={16} className="animate-spin" /> : saved ? <Check size={16} /> : null}
          {saved ? "Saved" : "Save Details"}
        </button>
      </div>
    </div>
  );
}
