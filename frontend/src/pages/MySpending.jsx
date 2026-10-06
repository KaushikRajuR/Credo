import { useState, useEffect } from "react";
import axios from "axios";
import { Plus, Loader2 } from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function MySpending() {
  const [amount, setAmount] = useState("");
  const [note, setNote] = useState("");
  const [isEssential, setIsEssential] = useState(true);
  const [saving, setSaving] = useState(false);
  const [entries, setEntries] = useState([]);
  const [summary, setSummary] = useState(null);

  const loadData = async () => {
    try {
      const [entriesRes, summaryRes] = await Promise.all([
        axios.get(`${API_URL}/api/spending/list`),
        axios.get(`${API_URL}/api/spending/summary`),
      ]);
      setEntries(entriesRes.data.entries);
      setSummary(summaryRes.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSave = async () => {
    if (!amount || !note) return;
    setSaving(true);
    try {
      await axios.post(`${API_URL}/api/spending/log`, {
        amount: Number(amount),
        note,
        is_essential: isEssential,
      });
      setAmount("");
      setNote("");
      setIsEssential(true);
      await loadData();
    } catch (err) {
      console.error(err);
    }
    setSaving(false);
  };

  return (
    <div className="px-6 py-8">
      <h2 className="text-2xl font-bold text-slate-800 mb-1">My Spending</h2>
      <p className="text-slate-500 mb-6">Log what you spend, whenever you spend it.</p>

      {/* Quick entry bar */}
      <div className="bg-white rounded-xl shadow-[0_1px_3px_rgba(0,0,0,0.06)] border border-slate-200 p-5 mb-6">
        <div className="flex gap-3">
          <input
            type="number"
            placeholder="Amount (₹)"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="w-32 px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-teal-500"
          />
          <input
            type="text"
            placeholder="What was it for? e.g. electricity bill"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            className="flex-1 px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-teal-500"
          />
          <button
            onClick={handleSave}
            disabled={saving || !amount || !note}
            className="px-4 py-2 bg-[#1e3a5f] text-white rounded-lg text-sm font-medium hover:bg-[#16293f] disabled:opacity-40 flex items-center gap-1.5 transition-colors"
          >
            {saving ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
            Save
          </button>
        </div>
        <label className="flex items-center gap-2 mt-3 text-sm text-slate-500">
          <input type="checkbox" checked={isEssential} onChange={(e) => setIsEssential(e.target.checked)} />
          This was an essential business expense
        </label>
      </div>

      {/* Summary */}
      {summary && summary.entry_count > 0 && (
        <div className="grid grid-cols-3 gap-4 mb-6">
          <SummaryCard label="Total Spent" value={`₹${summary.total_spent.toLocaleString()}`} />
          <SummaryCard label="Essential" value={`₹${summary.essential_spent.toLocaleString()}`} color="text-emerald-600" />
          <SummaryCard label="Discretionary" value={`₹${summary.discretionary_spent.toLocaleString()}`} color="text-amber-600" />
        </div>
      )}

      {/* Entry list */}
      <div className="bg-white rounded-xl shadow-[0_1px_3px_rgba(0,0,0,0.06)] border border-slate-200 divide-y divide-slate-100">
        {entries.length === 0 && (
          <p className="p-6 text-sm text-slate-400 text-center">No entries yet — log your first expense above.</p>
        )}
        {entries.map((e) => (
          <div key={e.id} className="flex justify-between items-center px-5 py-3">
            <div>
              <div className="text-sm font-medium text-slate-700">{e.note}</div>
              <div className="text-xs text-slate-400">
                {e.category} · {new Date(e.logged_at).toLocaleString()}
              </div>
            </div>
            <div className="text-sm font-semibold text-slate-800">₹{e.amount.toLocaleString()}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function SummaryCard({ label, value, color = "text-slate-800" }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-[0_1px_3px_rgba(0,0,0,0.06)] p-4">
      <div className="text-xs text-slate-400">{label}</div>
      <div className={`text-lg font-semibold ${color}`}>{value}</div>
    </div>
  );
}
