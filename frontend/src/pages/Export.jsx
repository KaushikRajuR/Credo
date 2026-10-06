import { useState } from "react";
import axios from "axios";
import { Download, Loader2, FileText } from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function Export() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleExport = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await axios.get(`${API_URL}/api/export/pdf`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([res.data], { type: "application/pdf" }));
      const link = document.createElement("a");
      link.href = url;
      link.download = "credo_financial_health_card.pdf";
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error(err);
      setError("Couldn't generate the export. Make sure My Details is filled in and you've computed a score at least once.");
    }
    setLoading(false);
  };

  return (
    <div className="px-6 py-8">
      <h2 className="text-2xl font-bold text-slate-800 mb-1">Export</h2>
      <p className="text-slate-500 mb-6">
        Download your Financial Health Card with your spending history.
      </p>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-8 text-center">
        <div className="w-14 h-14 bg-[#eef2f7] rounded-xl flex items-center justify-center mx-auto mb-4">
          <FileText className="text-[#1e3a5f]" size={28} />
        </div>
        <h3 className="font-semibold text-slate-700 mb-1">Financial Health Card</h3>
        <p className="text-sm text-slate-400 mb-6">
          Includes your current score, risk band, and your full spending history as a single PDF.
        </p>
        <button
          onClick={handleExport}
          disabled={loading}
          className="px-5 py-2.5 bg-[#1e3a5f] text-white rounded-lg text-sm font-medium hover:bg-[#16293f] disabled:opacity-50 inline-flex items-center gap-2"
        >
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Download size={16} />}
          {loading ? "Generating..." : "Download PDF"}
        </button>
        {error && <p className="text-sm text-red-500 mt-4">{error}</p>}
      </div>
    </div>
  );
}
